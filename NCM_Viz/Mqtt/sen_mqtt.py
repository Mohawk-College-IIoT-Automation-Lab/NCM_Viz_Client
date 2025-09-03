from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

import json
from Constants.base_models import SensorData
from Constants.configs import LoggerConfig, SenMQTT

class SenMQTT(GenericMQTT, QObject):
    _instance = None

    @classmethod
    def get_instance(cls, logger_config:LoggerConfig, parent=None):
        if cls._instance is None:
            cls._instance = cls(logger_config, parent)
        return cls._instance

    def __init__(self, logger_config:LoggerConfig, parent=None):

        if SenMQTT._instance is not None:
            logging.error("[SEN] Runtime Error: Trying to re-init SEN. use SenMQTT.get_instance(...)")
            raise RuntimeError("Use SenMQTT.get_instance() to access the singleton.")
        
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, client_name=self.__class__.__name__, log_name=logger_config.log_name, host_name=logger_config.mqtt_config.host_name, host_port=logger_config.mqtt_config.host_port)

        initialize_logging(process_name=logger_config.log_name, broker=logger_config.mqtt_config.host_name, port=logger_config.mqtt_config.host_port)

        logging.debug("[MQTT][SEN] Creating SENMQTT object")

        self.mqtt_connect()

    def _on_connect(self, client, userdata, flags, rc, props=None):
        logging.debug("f[MQTT][SEN] Subscribing to topic: " { Sen})

    def mqtt_json_callback(self, client:Client, userdata, msq:MQTTMessage):


