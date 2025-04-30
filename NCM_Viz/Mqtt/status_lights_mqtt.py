from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject
from Constants.configs import LoggerConfig, MQTTConfig, StatusLightsConfig

class StatusLightsMqtt(GenericMQTT, QObject):

    alarm_signal = pyqtSignal(str, bool)
    experiment_running = pyqtSignal(bool)
    experiment_elapsed_time = pyqtSignal(int)

    _instance = None
    
    @classmethod
    def get_instance(cls, logger_config:LoggerConfig = LoggerConfig, status_lights_config:StatusLightsConfig = StatusLightsConfig, parent=None):
        if cls._instance is None:
            cls._instance = cls(logger_config, status_lights_config, parent)
        return cls._instance

    def __init__(self, logger_config:LoggerConfig, status_lights_config:StatusLightsConfig, parent=None):

        if StatusLightsMqtt._instance is not None:
            logging.error("[QT][Status Lights] Runtime Error: Trying to re-init Status Lights. use StatusLightsMqtt.get_instance(...)")
            raise RuntimeError("Use StatusLightsMqtt.get_instance() to access the singleton.")

        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, log_name=logger_config.log_name, host_name=logger_config.mqtt_config.host_name, host_port=logger_config.mqtt_config.host_port)

        initialize_logging(process_name=logger_config.log_name, broker=logger_config.mqtt_config.host_name, port=logger_config.mqtt_config.host_port)

        logging.debug("Creating StatusLightsMqtt object")

        self.status_lights_config = status_lights_config

        for topic in status_lights_config.alarm_topics:
            topic = f"{status_lights_config.alarm_base_topic}{topic}"
            logging.debug(f"Subscribing to topic: {topic}")
            self.mqtt_client.message_callback_add(topic, self.mqtt_alarm_callback)
            self.mqtt_client.subscribe(topic)

        for topic in status_lights_config.experiment_topics:
            topic = f"{status_lights_config.experiment_base_topic}{topic}"
            logging.debug(f"Subscribing to topic: {topic}")
            self.mqtt_client.message_callback_add(topic, self.mqtt_experiment_callback)
            self.mqtt_client.subscribe(topic)
    
    def mqtt_experiment_callback(self, client:Client, userdata, message:MQTTMessage):
        if message.topic == "Running":
            self.experiment_running.emit(bool(message.payload))
            logging.info(f"[MQTT][ExperimentControl] Experiment Running: {message.payload}")

        elif message.topic == "ElapsedTime":
            try:
                elapsed_time = int(message.payload.decode())
                self.experiment_elapsed_time.emit(elapsed_time)
                logging.debug(f"[MQTT][ExperimentControl] Received data: {elapsed_time}")
            except ValueError:
                logging.error(f"[MQTT][ExperimentControl] Failed to decode elapsed time: {message.payload.decode()}")
        else:
            self._mqtt_default_callback(client, userdata, message)

    def mqtt_alarm_callback(self, client:Client, userdata, message:MQTTMessage):
        for word in self.status_lights_config.alarm_topics:
            if word in message.topic:
                self.alarm_signal.emit(word, message.payload.decode())
                logging.warning(f"[QT][Status Lights][MQTT] Alarm: {word} status: {message.payload.decode()}")
                return 
        else:
            logging.debug(f"[QT][Status Lights][MQTT] Missed a message?")
            self._mqtt_default_callback(client, userdata, message)
