from .GenericMqtteLogger.generic_mqtt import GenericMQTT, initialize_logging
import logging
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

class MouldControlMQTT(GenericMQTT, QObject):

    def __init__(self, log_name:str="Qt", host_name:str="localhost", host_port:int=1883, parent=None):
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, log_name=log_name, host_name=host_name, host_port=host_port)

        initialize_logging(process_name=log_name, broker=host_name, port=host_port)
        logging.debug(f"[MQTT][QT][Mould Control] Initializing MouldControlMQTT")