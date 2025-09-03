from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

import json
from Constants.base_models import SensorData
from Constants.configs import LoggerConfig, SensorsConfig, ExperimentMqttConfig


class SensorsMQTT(GenericMQTT, QObject):

    sensor_data_signal = pyqtSignal(SensorData)
    clear_plots_signal = pyqtSignal()

    _instance = None

    @classmethod
    def get_instance(cls, logger_config:LoggerConfig, parent=None):
        if cls._instance is None:
            cls._instance = cls(logger_config, parent)
        return cls._instance

    def __init__(self, logger_config:LoggerConfig, parent=None):

        if SensorsMQTT._instance is not None:
            logging.error("[Sensors] Runtime Error: Trying to re-init Sensors. use SensorsMQTT.get_instance(...)")
            raise RuntimeError("Use SensorsMQTT.get_instance() to access the singleton.")
        
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, client_name=self.__class__.__name__, log_name=logger_config.log_name, host_name=logger_config.mqtt_config.host_name, host_port=logger_config.mqtt_config.host_port)

        initialize_logging(process_name=logger_config.log_name, broker=logger_config.mqtt_config.host_name, port=logger_config.mqtt_config.host_port)

        logging.debug("[MQTT][Sensors] Creating SensorsMQTT object")

        self.mqtt_connect()

    def _on_connect(self, client, userdata, flags, rc, props=None):
        logging.debug(f"[MQTT][Sensors] Subscribing to topic: {SensorsConfig.display_data_topic}")
        client.subscribe(SensorsConfig.display_data_topic)
        client.message_callback_add(SensorsConfig.display_data_topic, self.mqtt_display_callback)

        topic = f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.start_topic}"
        logging.debug(f"[MQTT][Sensors] Subscribing to topic: {topic}")
        client.subscribe(topic)
        client.message_callback_add(topic, self.mqtt_clear_plots_callback)

    def mqtt_display_callback(self, client:Client, userdata, msg:MQTTMessage):
        try:
            sensor_data = SensorData.model_validate(json.loads(msg.payload.decode()))
            self.sensor_data_signal.emit(sensor_data)
            
        except json.JSONDecodeError:
            logging.error(f"[MQTT][SensorData] Failed to decode JSON payload: {msg.payload.decode()}")

    def mqtt_clear_plots_callback(self, client:Client, userdata, msg:MQTTMessage):
        logging.debug(f"[MQTT][Sensors] Clearing plots")
        self.clear_plots_signal.emit()
