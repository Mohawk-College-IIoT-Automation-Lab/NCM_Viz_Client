from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QStatusBar
from m_base_object import *


class M_QObject(QObject, M_Object):

    def __init__(self, status_bar:QStatusBar, host_name:str="localhost", host_port:int = 1883, log_name="log", parent=None):
        super().__init__(host_name, host_port, log_name, parent)
        self.status_bar = status_bar

        self.mqtt_client.on_message = self._mqtt_default_callback
        self.mqtt_client.on_connect = self._mqtt_connect_disconnect
        self.mqtt_client.on_disconnect = self._mqtt_connect_disconnect
        self.mqtt_client.on_connect_fail = self._mqtt_failed

    def _mqtt_connect_disconnect(self):
        # Get connection status
        self._connected = self.mqtt_client.is_connected()
        
        # Loop start/stop
        if self._connected:
            self.mqtt_client.loop_start()
        else:
            self.mqtt_client.loop_stop()

        # Loggign and emit status
        self.status_and_log(f"[MQTT] Connection status: {self.connected}")
        
    def _mqtt_failed(self):
        self.status_and_log("[MQTT] Failed to connect")

    def _mqtt_default_callback(self, client:Client, userdata, message:MQTTMessage):
        self.log(f"[MQTT] unhandled data received from topic: {message.topic} -> {message.payload.decode()}")

    def status_and_log(self, message:str):
        self.status_bar.showMessage(message)
        self.logger.debug(message)

    @pyqtSlot()
    def mqtt_connect(self):
        self.status_and_log(f"[MQTT] Attempting connection to host: {self._host_name} on port: {self._host_port}")

        error = self.mqtt_client.connect(self._host_name, self._host_port)
        
        if error:
            self.status_and_log(f"[MQTT] Error connecting to host: {self._host_name}:{self._host_port}, error code: {error}")
            
    @pyqtSlot()
    def mqtt_disconnect(self):
        self.log(f"Disconnecting from {self._host_name}:{self._host_port}")
        self.status_and_log(f"[MQTT] Disconnecting from host: {self._host_name}:{self._host_port}")

        self.mqtt_client.disconnect()


