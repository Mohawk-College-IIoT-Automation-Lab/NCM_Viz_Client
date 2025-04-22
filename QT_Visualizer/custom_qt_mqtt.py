from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
import json
from pydantic import BaseModel


class SensorReadings(BaseModel):
    LL: float
    LQ: float
    RR: float
    RQ: float
class SensorData(BaseModel):
    Ultra_Sonic_Distance: SensorReadings
    Anemometer: SensorReadings

class QMqtt(QObject):

    connected_signal = pyqtSignal(bool)
    status_bar_printer = pyqtSignal(str)

    def __init__(self, host_address:str="localhost", host_port:int=1883, parent=None):
        super().__init__(parent)
  
        self.host_addess = host_address
        self.host_port = host_port

        self.mqtt_client = Client()
        self.connection_status = False

        self.mqtt_client.on_message = self.mqtt_default_callback

        self.mqtt_client.on_connect = self._mqtt_connect_disconnect
        self.mqtt_client.on_disconnect = self._mqtt_connect_disconnect
        self.mqtt_client.on_connect_fail = self._mqtt_failed


    def _mqtt_connect_disconnect(self):
        self.connection_status = self.mqtt_client.is_connected()
        self.connected_signal.emit(self.connection_status)
        self.status_bar_printer.emit(f"[MQTT] Connection status: {self.connection_status}")

    def _mqtt_failed(self):
        self.status_bar_printer.emit("[MQTT] Failed to connect")

    @pyqtSlot()
    def connect(self):
        self.mqtt_client.connect(self.host_addess, self. host_port)
        self.status_bar_printer.emit(f"[MQTT] Attempting connection to host: {self.host_addess} on port: {self.host_port}")

    @pyqtSlot()
    def disconnect(self):
        self.mqtt_client.disconnect()
        self.status_bar_printer.emit("[MQTT] Disconnecting")

    def mqtt_default_callback(self, client:Client, userdata, message:MQTTMessage):
        self.status_bar_printer.emit(f"[MQTT] unhandled data received from topic: {message.topic} -> {message.payload.decode()}")

class QMqttSensors(QMqtt):

    distance_data_ready = pyqtSignal(float, float, float, float)
    anemometer_data_ready = pyqtSignal(float, float, float, float)

    def __init__(self, host_address:str="localhost", host_port:int=1883, parent=None):
        super().__init__(host_address, host_port, parent)

        self.display_data_topic = "NCM/DisplayData"

        self.mqtt_client.message_callback_add(self.display_data_topic, self.mqtt_display_callback)
        self.mqtt_client.subscribe(self.display_data_topic)
        
    def mqtt_display_callback(self, client:Client, userdata, message:MQTTMessage):
        try:
            payload = json.load(message.payload.decode())
            sensor_data = SensorData(**payload)

            self.distance_data_ready.emit(sensor_data.Ultra_Sonic_Distance.LL, sensor_data.Ultra_Sonic_Distance.LQ, sensor_data.Ultra_Sonic_Distance.RQ, sensor_data.Ultra_Sonic_Distance.RR)
            self.anemometer_data_ready.emit(sensor_data.Anemometer.LL, sensor_data.Anemometer.LQ, sensor_data.Anemometer.RQ, sensor_data.Anemometer.RR)
            
        except json.JSONDecodeError:
            self.status_bar_printer.emit(f"[MQTT][JSON Error] Loading / decoding error - Data: {message.payload.decode()}")

class QMqttAlarms(QMqtt):

    alarm_signal_1 = pyqtSignal(bool)
    alarm_signal_2 = pyqtSignal(bool)
    alarm_signal_3 = pyqtSignal(bool)
    alarm_signal_4 = pyqtSignal(bool)

    def __init__(self, host_address:str="localhost", host_port:int=1883, parent=None):
        super().__init__(host_address, host_port, parent)

        self.alarm_topic = "NCM/Alarm/#" # all alarm topics

        self.mqtt_client.message_callback_add(self.alarm_topic, self.mqtt_alarm_callback)
        self.mqtt_client.subscribe(self.alarm_topic)
    
    def mqtt_alarm_callback(self, client:Client, userdata, message:MQTTMessage):
        if message.topic == "Alarm1":
            self.alarm_signal_1.emit(bool(message.payload))
        elif message.topic == "Alarm2":
            self.alarm_signal_2.emit(bool(message.payload))
        elif message.topic == "Alarm3":
            self.alarm_signal_3.emit(bool(message.payload))
        elif message.topic == "Alarm4":
            self.alarm_signal_4.emit(bool(message.payload))
        else:
            self.mqtt_default_callback(client, userdata, message)
