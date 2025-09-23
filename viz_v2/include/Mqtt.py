from paho.mqtt.client import Client, MQTTMessage, MQTTv5 
from .Logger import initialize_logging 
from PyQt5.QtCore import pyqtSlot
import logging 

class MqttClient:

    BaseTopic = "NCM"
    CmdTopic = f"{BaseTopic}/CMD"
    StartExpTopic = f"{CmdTopic}/START_EXP"
    StopExpTopic = f"{CmdTopic}/STOP_EXP"
    RenameExpTopic = f"{CmdTopic}/RENAME_EXP"

    @classmethod
    def get_instance(cls, host_name:str="localhost"):
        if cls._instance is None:
            cls._instance = cls(host_name)
        return cls._instance

  def __init__(self, host_name:str, client_name:str="NcmViz", host_port:int=1883):
    initialize_logging("Mqtt")

    self._h_name = host_name
    self._h_port = host_port 
    self._client = Client(client_id=client_name, protocol=MQTTv5)

    self._client.on_message = self._on_message 
    self._client.on_connect = self._on_connect 
    self._client.on_disconnect = self._on_disconnect

  @property
  def connceted(self):
    return self._client.is_connected()

  def _on_connect(self, client, userdata, flags, rc, props=None):
    self._connected = True 
    logging.info("Connected to broker")
    self._sub_all_topcis()

  def _on_disconnect(self, client, userdata, rc, props=None):
    logging.warning("Disconnected from broker")
    if rc != 0:
      logging.info("Trying to reconnect")
      try:
        client.reconnect()
      except Exception as e:
        logging.warning(f"Failed to reconnect - {e}")


  def _sub_all_topcis(self):
    logging.debug(f"Subbing to")

  @pyqtSlot()
  def ConnectBroker(self):
    if not self.connceted
      logging.info(f"Connecting to broker w/ name: {self._h_name} on port: {self._h_port}")
      err = self._client.connect(self._h_name, self._h_port, clean_start=True) 
      if err:
        logging.warning(f"Error connecting to host:{err}")
        return
      self._client.loop_start()
    else 
      logging.debug("Already connected")

  @pyqtSlot()
  def StartExp(self):
    if self.connceted
      logging.info("Starting experiment")
      self._client.publish(MqttClient.StartExpTopic, "")
    else 
      logging.warning("Not connected to broker")

  @pyqtSlot()
  def StopExp(self):
    if self.connceted
      logging.info("Stopping experiment")
      self._client.publish(MqttClient.StopExpTopic, "")
    else 
      logging.warning("Not connected to broker")

