from re import S
from paho.mqtt.client import Client, MQTTv5, topic_matches_sub
import json
from PyQt5.QtCore import QTime, pyqtSignal, pyqtSlot, QTimer, QObject
from PyQt5.QtWidgets import QInputDialog, QWidget
import logging

from pydantic import BaseModel
from pathlib import Path

from .DataStructures import SenTelemetry, SenConfigModel, SensorData, SenPorts


class MqttClient(QWidget):

    BaseTopic = "NCM"
    CmdTopic = f"{BaseTopic}/CMD"
    StartExpTopic = f"{CmdTopic}/START_EXP"
    StopExpTopic = f"{CmdTopic}/STOP_EXP"
    RenameExpTopic = f"{CmdTopic}/RENAME_EXP"

    SenBaseTopic = f"{BaseTopic}/SEN"
    MoveToMMTopic = "goal/mm"
    MoveToPosTopic = "goal/position"
    MoveToPercentTopic = "goal/percent"
    JogPosTopic = "jog"
    StopTopic = "stop"
    HomeTopic = "home"
    SetHomeTopic = "set_home"
    GetConfigTopic = "get_config"
    MapPosTopic = "map"  # Need to check this
    TeleJsonTopic = "telemetery/json"

    # Sub
    TeleLJsonTopic = f"{SenBaseTopic}/LEFT/{TeleJsonTopic}"
    TeleRJsonTopic = f"{SenBaseTopic}/RIGHT/{TeleJsonTopic}"

    ConfigLTopic = f"{SenBaseTopic}/LEFT/config"
    ConfigRTopic = f"{SenBaseTopic}/RIGHT/config"

    DaqBaseTopic = f"{BaseTopic}/DAQ"
    DaqDataTopic = f"{DaqBaseTopic}/DisplayData"

    # signals

    ConnectedSignal = pyqtSignal(bool)
    DaqConnectedSignal = pyqtSignal(bool)
    LeftSenConnectedSignal = pyqtSignal(bool)
    RightSenConnectedSignal = pyqtSignal(bool)

    DaqDataSignal = pyqtSignal(SensorData)

    SenTeleLeftSignal = pyqtSignal(SenTelemetry)
    SenTeleRightSignal = pyqtSignal(SenTelemetry)

    SenLeftConfigSignal = pyqtSignal(SenConfigModel)
    SenRightConfigsignal = pyqtSignal(SenConfigModel)

    LOG_FMT_STR = f"[Mqtt] - %s"

    class Settings(BaseModel):
        host_name: str = "localhost"
        client_name: str = "NcmViz"
        host_port: int = 1883

    class Watchdog(QObject):

        CountSignal = pyqtSignal(int)
        TimeoutSignal = pyqtSignal()

        def __init__(
            self,
            name: str = "timer",
            interval: int = 100,
            autostart: bool = False,
            timeout: int = 2000,
            parent=None,
        ):
            super().__init__(parent)
            self.setObjectName(name)
            self._timer = QTimer()
            self._interval = interval
            self._en = autostart
            self._timeout = timeout
            self._counter = 0
            self._timer.setInterval(interval)
            self._timer.timeout.connect(self._bump_counter)

            self._timer.start()

        @property
        def count(self) -> int:
            return self._counter

        @property
        def enabled(self) -> bool:
            return self._en

        def _bump_counter(self):
            if self._en:
                self._counter += self._interval
                self.CountSignal.emit(self._counter)
                if self._counter > self._timeout > 0:
                    self.TimeoutSignal.emit()

        @pyqtSlot(bool)
        def ToggleTimer(self, en: bool):
            self._en = en

        @pyqtSlot()
        def ClearCounter(self):
            self._counter = 0

    _instance = None
    _settings = None
    _settings_file = None 
    _count = 0

    @classmethod
    def get_instance(cls, filename: str = "settings.json", parent=None):
        if cls._instance is None:
            
            logging.debug(MqttClient.LOG_FMT_STR, f"Cls counter: {cls._count}")

            cls._settings_file = Path(filename)
            if not cls._settings_file.exists():
                cls._make_settings_file(cls._settings_file)
            cls._settings = cls._load_setting_file(cls._settings_file)
            cls._instance = cls(cls._settings, parent)
        return cls._instance

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)

        self._h_name = settings.host_name
        self._h_port = settings.host_port

        logging.debug(
            MqttClient.LOG_FMT_STR,
            f"Creating Client Instance: name: {settings.client_name} host: {self._h_name}:{self._h_port}",
        )

        self._client = Client(client_id=settings.client_name, protocol=MQTTv5)

        self._daq_wdg = MqttClient.Watchdog(name="daq")
        self._daq_wdg.TimeoutSignal.connect(lambda: self.DaqConnectedSignal.emit(False))

        self._l_sen_wdg = MqttClient.Watchdog(name="lSen")
        self._l_sen_wdg.TimeoutSignal.connect(
            lambda: self.LeftSenConnectedSignal.emit(False)
        )

        self._r_sen_wdg = MqttClient.Watchdog(name="rSen")
        self._r_sen_wdg.TimeoutSignal.connect(
            lambda: self.RightSenConnectedSignal.emit(False)
        )

        self._daq_wdg.CountSignal.connect(lambda c: logging.debug(MqttClient.LOG_FMT_STR, f"{c} Daq Counter"))

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    @property
    def connected(self):
        return self._client.is_connected()

    @classmethod
    def _make_settings_file(
        cls, file: Path, host_name: str = "localhost", host_port: int = 1883
    ):
        _setting = MqttClient.Settings()
        file.write_text(_setting.model_dump_json(indent=2))

    @classmethod
    def _load_setting_file(cls, file: Path):
        return MqttClient.Settings.model_validate(json.loads(file.read_text()))

    def _on_connect(self, client, userdata, flags, rc, props=None):
        logging.info(MqttClient.LOG_FMT_STR, "Connected to broker")
        self._sub_all_topcis()
        self.ConnectedSignal.emit(True)

    def _on_disconnect(self, client, userdata, rc, props=None):
        logging.warning(MqttClient.LOG_FMT_STR, "Disconnected from broker")
        self.ConnectedSignal.emit(False)

        if rc != 0:
            logging.info(MqttClient.LOG_FMT_STR, "Trying to reconnect")
            try:
                client.reconnect()
            except Exception as e:
                logging.warning(MqttClient.LOG_FMT_STR, f"Failed to reconnect - {e}")
                self.ConnectedSignal.emit(False)

    def _sub_all_topcis(self):
        logging.debug(MqttClient.LOG_FMT_STR, f"Subbing all topics")

        self._client.subscribe(MqttClient.DaqDataTopic)
        self._client.subscribe(MqttClient.TeleLJsonTopic)
        self._client.subscribe(MqttClient.TeleRJsonTopic)
        self._client.subscribe(MqttClient.ConfigLTopic)
        self._client.subscribe(MqttClient.ConfigRTopic)

        self._client.message_callback_add(self.DaqDataTopic, self._DaqDataCallback)
        self._client.message_callback_add(self.TeleLJsonTopic, self._TeleLCallback)
        self._client.message_callback_add(self.TeleRJsonTopic, self._TeleRCallback)
        self._client.message_callback_add(self.ConfigLTopic, self._ConfigLCallback)
        self._client.message_callback_add(self.ConfigRTopic, self._ConfigRCallback)

    def _DaqDataCallback(self, client, userdata, msg):
        try:
            sensor_data = SensorData.model_validate(json.loads(msg.payload.decode()))
            self.DaqDataSignal.emit(sensor_data)

            self._daq_wdg.ClearCounter()
            self.DaqConnectedSignal.emit(True)
            if not self._daq_wdg.enabled:
                self._daq_wdg.ToggleTimer(True)

        except json.JSONDecodeError:
            logging.warning(
                MqttClient.LOG_FMT_STR,
                f"Failed to decode JSON payload: {msg.payload.decode()}",
            )

    def _TeleLCallback(self, client, userdata, msg):

        try:
            sen_tele = SenTelemetry.model_validate(json.loads(msg.payload.decode()))
            self.SenTeleLeftSignal.emit(sen_tele)

            self._l_sen_wdg.ClearCounter()
            self.LeftSenConnectedSignal.emit(True)
            if not self._l_sen_wdg.enabled:
                self._l_sen_wdg.ToggleTimer(True)

        except json.JSONDecodeError:
            logging.warning(
                MqttClient.LOG_FMT_STR,
                f"Failed to decode JSON payload: {msg.payload.decode()}",
            )

    def _TeleRCallback(self, client, userdata, msg):

        try:
            sen_tele = SenTelemetry.model_validate(json.loads(msg.payload.decode()))
            self.SenTeleRightSignal.emit(sen_tele)

            self._r_sen_wdg.ClearCounter()
            self.RightSenConnectedSignal.emit(True)
            if not self._r_sen_wdg.enabled:
                self._r_sen_wdg.ToggleTimer(True)

        except json.JSONDecodeError:
            logging.warning(
                MqttClient.LOG_FMT_STR,
                f"Failed to decode JSON payload: {msg.payload.decode()}",
            )

    def _ConfigLCallback(self, client, userdata, msg):
        try:
            sen_config = SenConfigModel.model_validate(json.loads(msg.payload.decode()))
            self.SenLeftConfigSignal.emit(sen_config)
        except json.JSONDecodeError:
            logging.warning(
                MqttClient.LOG_FMT_STR,
                f"Failed to decode JSON payload: {msg.payload.decode()}",
            )

    def _ConfigRCallback(self, client, userdata, msg):
        try:
            sen_config = SenConfigModel.model_validate(json.loads(msg.payload.decode()))
            self.SenRightConfigSignal.emit(sen_config)
        except json.JSONDecodeError:
            logging.warning(
                MqttClient.LOG_FMT_STR,
                f"Failed to decode JSON payload: {msg.payload.decode()}",
            )

    def _SenMoveToMM(self, port: SenPorts, mm: float):
        if self.connected:
            topic = f"{MqttClient.SenBaseTopic}/{port.value}/{MqttClient.MoveToMMTopic}"
            logging.info(MqttClient.LOG_FMT_STR, f"Moving {port.value} to MM: {mm} , topic: {topic}")
            self._client.publish(topic, mm)

        else:
            self._not_connected_warn()

    def _SenMoveToPos(self, port: SenPorts, pos: int):
        if self.connected:
            topic = f"{MqttClient.SenBaseTopic}/{port.value}/{MqttClient.MoveToPosTopic}"
            logging.info(MqttClient.LOG_FMT_STR, f"Moving {port.value} to pos: {pos}, topic: {topic}")
            self._client.publish(topic, pos)
        else:
            self._not_connected_warn()

    def _SenMoveToPercent(self, port: SenPorts, percent: int):
        if self.connected:
            topic = f"{MqttClient.SenBaseTopic}/{port.value}/{MqttClient.MoveToPercentTopic}"
            logging.info(MqttClient.LOG_FMT_STR, f"Moving {port.value} to percent: {percent}, topic: {topic}")

            self._client.publish(topic, percent)
        else:
            self._not_connected_warn()


    def _SenJog(self, port: SenPorts, pos: int | None = None):
        if self.connected:
            topic = f"{MqttClient.SenBaseTopic}/{port.value}/{MqttClient.JogPosTopic}"
            logging.info(MqttClient.LOG_FMT_STR, f"Jogging {pos} steps, topic: {topic}")

            self._client.publish(topic, pos)

        else:
            self._not_connected_warn()

    def _SenMapPos(self, port: SenPorts, mm: float | None = None):
        if self.connected:
            topic = f"{MqttClient.SenBaseTopic}/{port.value}/{MqttClient.MapPosTopic}"
            logging.info(MqttClient.LOG_FMT_STR, f"Mapping {mm} to current position, topic: {topic}")

            self._client.publish(topic, mm)
        else:
            self._not_connected_warn()

    def _SenGetConfig(self, port: SenPorts):
        if self.connected:
            topic = f"{MqttClient.SenBaseTopic}/{port.value}/{MqttClient.GetConfigTopic}"
            self._client.publish(topic, "")
        else:
            self._not_connected_warn()

    def _SenSetHome(self, port: SenPorts):
        if self.connected:
            topic = f"{MqttClient.SenBaseTopic}/{port.value}/{MqttClient.SetHomeTopic}"
            self._client.publish(topic, "")
        else:
            self._not_connected_warn()

    def _not_connected_warn(self):
        logging.warning(MqttClient.LOG_FMT_STR, "Not connected to broker")

    @pyqtSlot()
    def DisconnectBroker(self):
        if self.connected:
            logging.info(
                MqttClient.LOG_FMT_STR, f"Disconnecting from broker {self._h_name}"
            )
            err = self._client.disconnect()
            self._client.loop_stop()
            if err:
                logging.warning(
                    MqttClient.LOG_FMT_STR, f"Error disconnecting from broker: {err}"
                )
        else:
            logging.debug(MqttClient.LOG_FMT_STR, "Not connected anyways")

    @pyqtSlot()
    def ConnectBroker(self):
        if not self.connected:
            logging.info(
                MqttClient.LOG_FMT_STR,
                f"Connecting to broker w/ name: {self._h_name} on port: {self._h_port}",
            )
            err = self._client.connect(self._h_name, self._h_port, clean_start=True)
            if err:
                logging.warning(
                    MqttClient.LOG_FMT_STR, f"Error connecting to host:{err}"
                )
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

    @pyqtSlot()
    def RenameExp(self, filename: str | None = None):
        if self.connected:
            if filename is None:
                value, ok = QInputDialog.getText(
                    self, title="Rename file", label="File name:"
                )

                if ok:
                    if value:
                        filename = value
                    else:
                        logging.warning(
                            MqttClient.LOG_FMT_STR, "Filename was left empty"
                        )
                        return
                else:
                    logging.debug(MqttClient.LOG_FMT_STR, "User cancelled name change")
                    return
            logging.info(MqttClient.LOG_FMT_STR, f"Renaming file to: {filename}")
            self._client.publish(MqttClient.RenameExpTopic, filename)
        else:
            self._not_connected_warn()

    @pyqtSlot(float)
    def SenLMoveToMM(self, mm: float):
        self._SenMoveToMM(SenPorts.LeftPort, mm)

    @pyqtSlot(float)
    def SenRMoveToMM(self, mm: float):
        self._SenMoveToMM(SenPorts.RightPort, mm)

    @pyqtSlot(int)
    def SenLMoveToPos(self, pos: int):
        self._SenMoveToPos(SenPorts.LeftPort, pos)

    @pyqtSlot(int)
    def SenRMoveToPos(self, pos: int):
        self._SenMoveToPos(SenPorts.RightPort, pos)

    @pyqtSlot(int)
    def SenLMovePercent(self, percent:int):
        self._SenMoveToPercent(SenPorts.LeftPort, percent)

    @pyqtSlot(int)
    def SenRMovePercent(self, percent:int):
        self._SenMoveToPercent(SenPorts.RightPort, percent)

    @pyqtSlot(int)
    def SenLJog(self, pos: int):
        self._SenJog(SenPorts.LeftPort, pos)

    @pyqtSlot(int)
    def SenRJog(self, pos: int):
        self._SenJog(SenPorts.RightPort, pos)

    @pyqtSlot(float)
    def SenLMapPos(self, mm: float):
        self._SenMapPos(SenPorts.LeftPort, mm)

    @pyqtSlot()
    def SenRMapPos(self, mm: float):
        self._SenMapPos(SenPorts.RightPort, mm)

    @pyqtSlot()
    def SenGetLConfig(self):
        self._SenGetConfig(SenPorts.LeftPort)

    @pyqtSlot()
    def SenGetRConfig(self):
        self._SenGetConfig(SenPorts.RightPort)

    @pyqtSlot()
    def SenSetLHome(self):
        self._SenSetHome(SenPorts.LeftPort)

    @pyqtSlot()
    def SeNSetRHome(self):
        self._SenSetHome(SenPorts.RightPort)
