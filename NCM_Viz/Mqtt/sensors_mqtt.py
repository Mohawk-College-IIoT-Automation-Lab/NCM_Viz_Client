from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

import json
from pydantic import BaseModel
from Constants.base_models import SensorData, SensorReadings
from Constants.configs import LoggerConfig, MQTTConfig, SensorsConfig


class SensorsMQTT(GenericMQTT, QObject):

    distance_data_ready = pyqtSignal(float, float, float, float)
    anemometer_data_ready = pyqtSignal(float, float, float, float)

    _instance = None

    @classmethod
    def get_instance(cls, logger_config:LoggerConfig = LoggerConfig, sensors_config:SensorsConfig = SensorsConfig, parent=None):
        if cls._instance is None:
            cls._instance = cls(logger_config, parent)
        return cls._instance

    def __init__(self, logger_config:LoggerConfig, sensors_config:SensorsConfig, parent=None):

        if SensorsMQTT._instance is not None:
            logging.error("[QT][Sensors] Runtime Error: Trying to re-init Sensors. use SensorsMQTT.get_instance(...)")
            raise RuntimeError("Use SensorsMQTT.get_instance() to access the singleton.")
        
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, log_name=logger_config.log_name, host_name=logger_config.mqtt_config.host_name, host_port=logger_config.mqtt_config.host_port)

        initialize_logging(process_name=logger_config.log_name, broker=logger_config.mqtt_config.host_name, port=logger_config.mqtt_config.host_port)

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