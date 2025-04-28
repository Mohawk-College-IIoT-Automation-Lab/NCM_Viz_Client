from .GenericMqtteLogger.generic_mqtt import GenericMQTT, Logger
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

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

class SensorsMQTT(GenericMQTT, QObject):

    distance_data_ready = pyqtSignal(float, float, float, float)
    anemometer_data_ready = pyqtSignal(float, float, float, float)
    
    def __init__(self, host_address:str="localhost", host_port:int=1883, logger:Logger=None, parent=None):
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, host_address, host_port, logger)

        self.logger.debug("Creating SensorsMQTT object")

        self.display_data_topic = "NCM/SensorData"

        self.logger.debug(f"Subscribing to topic: {self.display_data_topic}")
        
        self.mqtt_client.message_callback_add(self.display_data_topic, self.mqtt_display_callback)
        self.mqtt_client.subscribe(self.display_data_topic)
        
    def mqtt_display_callback(self, client:Client, userdata, message:MQTTMessage):
        try:
            payload = json.load(message.payload.decode())
            sensor_data = SensorData(**payload)

            self.logger.info(f"[MQTT][SensorData] Received data: {sensor_data}")

            self.distance_data_ready.emit(sensor_data.Ultra_Sonic_Distance.LL, sensor_data.Ultra_Sonic_Distance.LQ, sensor_data.Ultra_Sonic_Distance.RQ, sensor_data.Ultra_Sonic_Distance.RR)
            self.anemometer_data_ready.emit(sensor_data.Anemometer.LL, sensor_data.Anemometer.LQ, sensor_data.Anemometer.RQ, sensor_data.Anemometer.RR)
            
        except json.JSONDecodeError:
            self.logger.error(f"[MQTT][SensorData] Failed to decode JSON payload: {message.payload.decode()}")