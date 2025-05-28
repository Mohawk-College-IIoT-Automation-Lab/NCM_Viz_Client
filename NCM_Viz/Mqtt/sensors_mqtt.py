from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

import json
from pydantic import BaseModel
from Constants.base_models import SensorData, SensorReadings
from Constants.configs import LoggerConfig, MQTTConfig, SensorsConfig, ExperimentMqttConfig


class SensorsMQTT(GenericMQTT, QObject):

    distance_data_ready = pyqtSignal(float, float, float, float)
    anemometer_data_ready = pyqtSignal(float, float, float, float)
    standing_wave_ready = pyqtSignal(float, float)
    clear_plots_signal = pyqtSignal()

    _instance = None

    @classmethod
    def get_instance(cls, logger_config:LoggerConfig, parent=None):
        if cls._instance is None:
            cls._instance = cls(logger_config, parent)
        return cls._instance

    def __init__(self, logger_config:LoggerConfig, parent=None):

        if SensorsMQTT._instance is not None:
            logging.error("[QT][Sensors] Runtime Error: Trying to re-init Sensors. use SensorsMQTT.get_instance(...)")
            raise RuntimeError("Use SensorsMQTT.get_instance() to access the singleton.")
        
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, client_name="SensorsMQTT", log_name=logger_config.log_name, host_name=logger_config.mqtt_config.host_name, host_port=logger_config.mqtt_config.host_port)

        initialize_logging(process_name=logger_config.log_name, broker=logger_config.mqtt_config.host_name, port=logger_config.mqtt_config.host_port)

        logging.debug("[QT][MQTT][Sensors] Creating SensorsMQTT object")

        self.mqtt_connect()

    def _on_connect(self, client, userdata, flags, rc, props=None):
        logging.debug(f"[QT][Sensors] Subscribing to topic: {SensorsConfig.display_data_topic}")
        client.subscribe(SensorsConfig.display_data_topic)
        client.message_callback_add(SensorsConfig.display_data_topic, self.mqtt_display_callback)

        topic = f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.start_topic}"
        logging.debug(f"[QT][Sensors] Subscribing to topic: {topic}")
        client.subscribe(topic)
        client.message_callback_add(topic, self.mqtt_clear_plots_callback)

    def mqtt_display_callback(self, client:Client, userdata, msg:MQTTMessage):
        try:
            sensor_data = SensorData.model_validate(json.loads(msg.payload.decode()))
            self.distance_data_ready.emit(sensor_data.Ultra_Sonic_Distance.LL, sensor_data.Ultra_Sonic_Distance.LQ, sensor_data.Ultra_Sonic_Distance.RQ, sensor_data.Ultra_Sonic_Distance.RR)
            self.anemometer_data_ready.emit(sensor_data.Anemometer.LL, sensor_data.Anemometer.LQ, sensor_data.Anemometer.RQ, sensor_data.Anemometer.RR)
            self.standing_wave_ready.emit(sensor_data.Standing_Wave.Left, sensor_data.Standing_Wave.Right)
            
        except json.JSONDecodeError:
            logging.error(f"[QT][MQTT][SensorData] Failed to decode JSON payload: {msg.payload.decode()}")

    def mqtt_clear_plots_callback(self, client:Client, userdata, msg:MQTTMessage):
        logging.debug(f"[QT][Sensors] Clearing plots")
        self.clear_plots_signal.emit()
