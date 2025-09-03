from os import sendfile
from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

import json
from Constants.base_models import XM430Telemetery, XM430Config
from Constants.configs import LoggerConfig, Sen1MqttConfig, Sen2MqttConfig


class SenMQTT(GenericMQTT, QObject):
    
    sen1_telemetery_data = pyqtSignal(XM430Telemetery)
    sen2_telemetery_data = pyqtSignal(XM430Telemetery)
    sen1_config_data = pyqtSignal(XM430Config)
    sen2_config_data = pyqtSignal(XM430Config)

    _instance = None


    @classmethod
    def get_instance(cls, logger_config: LoggerConfig, parent=None):
        if cls._instance is None:
            cls._instance = cls(logger_config, parent)
        return cls._instance


    def __init__(self, logger_config: LoggerConfig, parent=None):

        if SenMQTT._instance is not None:
            logging.error(
                "[SEN] Runtime Error: Trying to re-init SEN. use SenMQTT.get_instance(...)"
            )
            raise RuntimeError("Use SenMQTT.get_instance() to access the singleton.")

        QObject.__init__(self, parent)
        GenericMQTT.__init__(
            self,
            client_name=self.__class__.__name__,
            log_name=logger_config.log_name,
            host_name=logger_config.mqtt_config.host_name,
            host_port=logger_config.mqtt_config.host_port,
        )

        initialize_logging(
            process_name=logger_config.log_name,
            broker=logger_config.mqtt_config.host_name,
            port=logger_config.mqtt_config.host_port,
        )

        logging.debug("[MQTT][SEN] Creating SENMQTT object")

        self.mqtt_connect()

    def _on_connect(self, client, userdata, flags, rc, props=None):
        topic = f"{Sen1MqttConfig.base_topic}{Sen1MqttConfig.config_topic}"
        logging.debug(f"[MQTT][SEN] Subscribing to topic: {topic}")
        client.subscribe(topic)
        client.message_callback_add(
            topic,
            lambda self, client, userdata, msg: self.mqtt_config_callback(
                self, 1, client, userdata, msg
            ),
        )

        topic = f"{Sen2MqttConfig.base_topic}{Sen2MqttConfig.config_topic}"
        logging.debug(f"[MQTT][SEN] Subscribing to topic: {topic}")
        client.subscribe(topic)
        client.message_callback_add(
            topic,
            lambda self, client, userdata, msg: self.mqtt_config_callback(
                self, 2, client, userdata, msg
            ),
        )

        topic = f"{Sen1MqttConfig.base_topic}{Sen1MqttConfig.telemetery_json_topic}"
        logging.debug(f"[MQTT][SEN] Subscribing to topic: {topic}")
        client.subscribe(topic)
        client.message_callback_add(
            topic,
            lambda self, client, userdata, msg: self.mqtt_json_callback(
                self, 1, client, userdata, msg
            ),
        )

        topic = f"{Sen2MqttConfig.base_topic}{Sen2MqttConfig.telemetery_json_topic}"
        logging.debug(f"[MQTT][SEN] Subscribing to topic: {topic}")
        client.subscribe(topic)
        client.message_callback_add(
            topic,
            lambda self, client, userdata, msg: self.mqtt_json_callback(
                self, 2, client, userdata, msg
            ),
        )

    def mqtt_json_callback(self, id: int, client: Client, userdata, msg: MQTTMessage):
        try: 
            sen_tele = XM430Telemetery.model_validate(json.loads(msg.payload.decode()))
            if id == 1 :
                self.sen1_telemetery_data.emit(sen_tele)
            else: 
                self.sen2_telemetery_data.emit(sen_tele)
        except json.JSONDecodeError:
           logging.error(f"[MQTT][SEN] Failed to decode JSON payload: {msg.payload.decode()}")

    def mqtt_config_callback(self, id: int, client: Client, userdata, msg: MQTTMessage):
        pass
