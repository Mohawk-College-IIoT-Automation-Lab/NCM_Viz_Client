from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject
from Constants.configs import LoggerConfig, MQTTConfig, StatusLightsConfig, ExperimentMqttConfig

class StatusLightsMqtt(GenericMQTT, QObject):

    alarm_signal = pyqtSignal(str, bool)
    experiment_running = pyqtSignal(bool)
    experiment_elapsed_time = pyqtSignal(int)

    _instance = None
    
    @classmethod
    def get_instance(cls, logger_config:LoggerConfig = LoggerConfig, parent=None):
        if cls._instance is None:
            cls._instance = cls(logger_config, parent)
        return cls._instance

    def __init__(self, logger_config:LoggerConfig, parent=None):

        if StatusLightsMqtt._instance is not None:
            logging.error("[QT][Status Lights] Runtime Error: Trying to re-init Status Lights. use StatusLightsMqtt.get_instance(...)")
            raise RuntimeError("Use StatusLightsMqtt.get_instance() to access the singleton.")

        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, client_name="StatusMQTT", log_name=logger_config.log_name, host_name=logger_config.mqtt_config.host_name, host_port=logger_config.mqtt_config.host_port)

        initialize_logging(process_name=logger_config.log_name, broker=logger_config.mqtt_config.host_name, port=logger_config.mqtt_config.host_port)

        logging.debug("[QT][MQTT][Status Lights][init] Creating StatusLightsMqtt object")

        self.mqtt_connect()

    def _mqtt_connect_disconnect(self, client, userdata, flags, reason_code):
        super()._mqtt_connect_disconnect(client, userdata, flags, reason_code)

        if self.connected:  
            self.mqtt_client.subscribe(f"{StatusLightsConfig.alarm_base_topic}#")
            self.mqtt_client.subscribe(f"{ExperimentMqttConfig.base_topic}#")

            for topic in StatusLightsConfig.alarm_topics:
                topic = f"{StatusLightsConfig.alarm_base_topic}{topic}"
                logging.debug(f"[QT][MQTT][Status Lights][init] Subscribing to topic: {topic}")
                self.mqtt_client.message_callback_add(topic, self.mqtt_alarm_callback)

            topic = f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.start_topic}"
            logging.debug(f"[QT][MQTT][Experiment Control][init] Subscribing to topic: {topic}")
            self.mqtt_client.message_callback_add(topic, self.mqtt_experiment_callback)

            topic = f"{ExperimentMqttConfig.base_topic}{ExperimentMqttConfig.stop_topic}"
            logging.debug(f"[QT][MQTT][Experiment Control][init] Subscribing to topic: {topic}")
            self.mqtt_client.message_callback_add(topic, self.mqtt_experiment_callback)
    

    
    def mqtt_experiment_callback(self, client:Client, userdata, message:MQTTMessage):
        if ExperimentMqttConfig.start_topic in message.topic:
            self.experiment_running.emit(True)
            logging.info(f"[MQTT][Experiment Control] Experiment Started")
        elif ExperimentMqttConfig.stop_topic in message.topic:
            self.experiment_running.emit(False)
            logging.info(f"[MQTT][Experiment Control] Experiment Stopped")
        elif ExperimentMqttConfig.elapsed_topic in message.topic:
            try:
                elapsed_time = int(message.payload.decode())
                self.experiment_elapsed_time.emit(elapsed_time)
                logging.debug(f"[MQTT][Experiment Control] Received data: {elapsed_time}")
            except ValueError:
                logging.error(f"[MQTT][Experiment Control] Failed to decode elapsed time: {message.payload.decode()}")
        else:
            self._mqtt_default_callback(client, userdata, message)

    def mqtt_alarm_callback(self, client:Client, userdata, message:MQTTMessage):
        topic = message.topic.replace(StatusLightsConfig.alarm_base_topic)
        self.alarm_signal.emit(topic, message.payload.decode())
        logging.debug(f"[QT][MQTT][Status Lights] Received alarm: {topic}")