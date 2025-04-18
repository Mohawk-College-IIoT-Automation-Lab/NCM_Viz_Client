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

class QMqttObject(QObject):

    distance_data_ready = pyqtSignal(float, float, float, float)
    anemometer_data_ready = pyqtSignal(float, float, float, float)

    def __init__(self, host_address:str, host_port:int, parent=None):
        super().__init__(parent)
  
        self.host_addess = host_address
        self.host_port = host_port

        self.mqtt_client = Client()
        #self.mqtt_client.connect(self.host_addess, self.host_port)
        
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_connect_fail = self.mqtt_connect_fail
        self.mqtt_client.on_message = self.mqtt_default_callback
        self.mqtt_client.message_callback_add("NCM/DisplayData", self.mqtt_display_callback)
        self.mqtt_client.message_callback_add("NCM/Control/#", self.mqtt_control_callback)

    
    def mqtt_on_connect(self):
        self.mqtt_client.subscribe("NCM/DisplayData")
        self.mqtt_client.subscribe("NCM/Control/#")
        self.mqtt_client.subscribe("NCM/#")
        print(f"[Mqtt] Connection Success to Host: {self.host_addess} on Port: {self.host_port}")

    def mqtt_connect_fail(self):
        print(f"[Mqtt Error] Connection Failed to Host: {self.host_addess} on Port: {self.host_port}")
    
    def mqtt_display_callback(self, client:Client, userdata, message:MQTTMessage):
        try:
            payload = json.load(message.payload.decode())
            sensor_data = SensorData(**payload)

            self.data_available_signal.emit(sensor_data.Ultra_Sonic_Distance.LL, sensor_data.Ultra_Sonic_Distance.LQ, sensor_data.Ultra_Sonic_Distance.RQ, sensor_data.Ultra_Sonic_Distance.RR)
            
        except json.JSONDecodeError:
            print(f"[JSON Error] Loading / decoding error - Data: {message.payload.decode()}")


    def mqtt_control_callback(self, client:Client, userdata, message:MQTTMessage):
        pass

    def mqtt_default_callback(self, client:Client, userdata, message:MQTTMessage):
        print(f"[MQTT Message Received] Topic: {message.topic} Data: {message.payload.decode()}")




