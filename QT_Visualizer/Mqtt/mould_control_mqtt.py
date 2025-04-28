from .GenericMqtteLogger.generic_mqtt import GenericMQTT, Logger
from paho.mqtt.client import Client, MQTTMessage
from PyQt5.QtCore import pyqtSignal, QObject

class MouldControlMQTT(GenericMQTT, QObject):

    def __init__(self, host_address:str="localhost", host_port:int=1883, logger:Logger=None, parent=None):
        QObject.__init__(self, parent)
        GenericMQTT.__init__(self, host_address, host_port, logger)