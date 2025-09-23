from paho.mqtt.client import MQTT_CLIENT, Client, MQTTMessage, MQTTv5

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QInputDialog, QWidget
import logging


class MqttClient(QWidget):

    BaseTopic = "NCM"
    CmdTopic = f"{BaseTopic}/CMD"
    StartExpTopic = f"{CmdTopic}/START_EXP"
    StopExpTopic = f"{CmdTopic}/STOP_EXP"
    RenameExpTopic = f"{CmdTopic}/RENAME_EXP"

    LOG_FMT_STR = f"[Mqtt] - %s"


    _instance = None

    @classmethod
    def get_instance(cls, host_name: str = "localhost", parent=None):
        if cls._instance is None:
            cls._instance = cls(host_name, parent)
        return cls._instance

    def __init__(
        self,
        host_name: str,
        client_name: str = "NcmViz",
        host_port: int = 1883,
        parent=None,
    ):
        super().__init__(parent)


        self._h_name = host_name
        self._h_port = host_port
        self._client = Client(client_id=client_name, protocol=MQTTv5)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    @property
    def connected(self):
        return self._client.is_connected()

    def _on_connect(self, client, userdata, flags, rc, props=None):
        logging.info(MqttClient.LOG_FMT_STR, "Connected to broker")
        self._sub_all_topcis()

    def _on_disconnect(self, client, userdata, rc, props=None):
        logging.warning(MqttClient.LOG_FMT_STR, "Disconnected from broker")
        if rc != 0:
            logging.info(MqttClient.LOG_FMT_STR, "Trying to reconnect")
            try:
                client.reconnect()
            except Exception as e:
                logging.warning(MqttClient.LOG_FMT_STR, f"Failed to reconnect - {e}")

    def _sub_all_topcis(self):
        logging.debug(MqttClient.LOG_FMT_STR, f"Subbing")

    def _not_connected_warn(self):
        logging.warning(MqttClient.LOG_FMT_STR, "Not connected to broker")

    @pyqtSlot()
    def DisconnectBroker(self):
        if self.connected:
            logging.info(MqttClient.LOG_FMT_STR, f"Disconnecting from broker {self._h_name}")
            self._client.loop_stop()
            err = self._client.disconnect()
            if err:
                logging.warning(MqttClient.LOG_FMT_STR, f"Error disconnecting from broker: {err}")
        else:
            logging.debug(MqttClient.LOG_FMT_STR, "Not connected anyways")

    @pyqtSlot()
    def ConnectBroker(self):
        if not self.connceted:
            logging.info(MqttClient.LOG_FMT_STR, 
                f"Connecting to broker w/ name: {self._h_name} on port: {self._h_port}"
            )
            err = self._client.connect(self._h_name, self._h_port, clean_start=True)
            if err:
                logging.warning(MqttClient.LOG_FMT_STR, f"Error connecting to host:{err}")
                return
            self._client.loop_start()
        else:
            logging.debug(MqttClient.LOG_FMT_STR, "Already connected")

    @pyqtSlot()
    def StartExp(self):
        if self.connected:
            logging.info(MqttClient.LOG_FMT_STR, "Starting experiment")
            self._client.publish(MqttClient.StartExpTopic, "")
        else:
            self._not_connected_warn()

    @pyqtSlot()
    def StopExp(self):
        if self.connected:
            logging.info(MqttClient.LOG_FMT_STR, "Stopping experiment")
            self._client.publish(MqttClient.StopExpTopic, "")
        else:
            self._not_connected_warn()

    @pyqtSlot(str)
    def RenameExp(self, filename:str|None):
        if self.connected:
            if not filename:
                value, ok = QInputDialog.getText(
                    self, title="Rename file", label="File name:"
                )

                if ok:
                    if value:
                        filename = value
                    else:
                        logging.warning(MqttClient.LOG_FMT_STR, "Filename was left empty")
                        return
                else:
                    logging.debug(MqttClient.LOG_FMT_STR, "User cancelled name change")
                    return

            logging.info(MqttClient.LOG_FMT_STR, f"Renaming file to: {filename}")
            self._client.publish(MqttClient.RenameExpTopic, filename)
        else:
            self._not_connected_warn()

    @pyqtSlot(float)
    def SenMoveToMM(mm:float|None):

