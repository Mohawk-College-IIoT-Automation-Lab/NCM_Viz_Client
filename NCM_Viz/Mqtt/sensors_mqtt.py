from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
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
    
    def __init__(self, log_name:str="Qt", host_name:str="localhost", host_port:int=1883, parent=None):
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, log_name=log_name, host_name=host_name, host_port=host_port)

        initialize_logging(process_name=log_name, broker=host_name, port=host_port)

        logging.debug("Creating SensorsMQTT object")

        self.display_data_topic = "NCM/SensorData"

        logging.debug(f"Subscribing to topic: {self.display_data_topic}")
        
        self.mqtt_client.message_callback_add(self.display_data_topic, self.mqtt_display_callback)
        self.mqtt_client.subscribe(self.display_data_topic)
        
    def mqtt_display_callback(self, client:Client, userdata, message:MQTTMessage):
        try:
            payload = json.load(message.payload.decode())
            sensor_data = SensorData(**payload)

            logging.info(f"[MQTT][SensorData] Received data: {sensor_data}")

            self.distance_data_ready.emit(sensor_data.Ultra_Sonic_Distance.LL, sensor_data.Ultra_Sonic_Distance.LQ, sensor_data.Ultra_Sonic_Distance.RQ, sensor_data.Ultra_Sonic_Distance.RR)
            self.anemometer_data_ready.emit(sensor_data.Anemometer.LL, sensor_data.Anemometer.LQ, sensor_data.Anemometer.RQ, sensor_data.Anemometer.RR)
            
        except json.JSONDecodeError:
            logging.error(f"[MQTT][SensorData] Failed to decode JSON payload: {message.payload.decode()}")