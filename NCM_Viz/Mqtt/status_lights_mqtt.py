from .GenericMqtteLogger.generic_mqtt import GenericMQTT, Logger
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

class StatusLightsMqtt(GenericMQTT, QObject):

    alarm_signal_1 = pyqtSignal(bool)
    alarm_signal_2 = pyqtSignal(bool)
    alarm_signal_3 = pyqtSignal(bool)
    alarm_signal_4 = pyqtSignal(bool)

    experiment_running = pyqtSignal(bool)
    experiment_elapsed_time = pyqtSignal(int)
    
    def __init__(self, host_address:str="localhost", host_port:int=1883, logger:Logger=None, parent=None):
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, host_address, host_port, logger)
        self.logger.debug("Creating QMqttAlarms object")

        self.alarm_base_topic = "NCM/Alarm/"
        self.alarm_topcis = [f"{self.alarm_base_topic}Alarm{i}" for i in range(1, 4)]

        self.experiment_base_topic = "NCM/ExperimentControl/" # all experiment control topics
        self.experiment_topics = [f"{self.experiment_base_topic}Running", f"{self.experiment_base_topic}ElapsedTime"]

        for topic in self.alarm_topcis:
            self.logger.debug(f"Subscribing to topic: {topic}")
            self.mqtt_client.message_callback_add(topic, self.mqtt_alarm_callback)
            self.mqtt_client.subscribe(topic)

        for topic in self.experiment_topics:
            self.logger.debug(f"Subscribing to topic: {topic}")
            self.mqtt_client.message_callback_add(topic, self.mqtt_alarm_callback)
            self.mqtt_client.subscribe(topic)
    
    def mqtt_experiment_callback(self, client:Client, userdata, message:MQTTMessage):
        if message.topic == "Running":
            self.experiment_running.emit(bool(message.payload))
            self.logger.info(f"[MQTT][ExperimentControl] Experiment Running: {message.payload}")

        elif message.topic == "ElapsedTime":
            try:
                elapsed_time = int(message.payload.decode())
                self.experiment_elapsed_time.emit(elapsed_time)
                self.logger.debug(f"[MQTT][ExperimentControl] Received data: {elapsed_time}")
            except ValueError:
                self.logger.error(f"[MQTT][ExperimentControl] Failed to decode elapsed time: {message.payload.decode()}")
        else:
            self._mqtt_default_callback(client, userdata, message)

    def mqtt_alarm_callback(self, client:Client, userdata, message:MQTTMessage):
        if message.topic == "Alarm1":
            self.alarm_signal_1.emit(bool(message.payload))
            self.logger.info(f"[MQTT][Alarm1] Received data: {message.payload}")

        elif message.topic == "Alarm2":
            self.alarm_signal_2.emit(bool(message.payload))
            self.logger.info(f"[MQTT][Alarm2] Received data: {message.payload}")

        elif message.topic == "Alarm3":
            self.alarm_signal_3.emit(bool(message.payload))
            self.logger.info(f"[MQTT][Alarm3] Received data: {message.payload}")

        elif message.topic == "Alarm4":
            self.alarm_signal_4.emit(bool(message.payload))
            self.logger.info(f"[MQTT][Alarm4] Received data: {message.payload}")
            
        else:
            self._mqtt_default_callback(client, userdata, message)
