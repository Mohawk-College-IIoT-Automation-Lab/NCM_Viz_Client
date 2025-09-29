import logging
from PyQt5.QtCore import pyqtSlot, right
from PyQt5.QtWidgets import QAction, QMenuBar, QInputDialog

from .Mqtt import MqttClient


class MenuBar(QMenuBar):

    CloseAppAction = QAction("Close App")
    ConnectMqttAction = QAction("Conect Mqtt")
    DisconnectMqttAction = QAction("Disconnect Mqtt")

    StartExpAction = QAction("Start Experiment")
    RenameExpAction = QAction("Rename Experiment")
    StopExpAction = QAction("Stop Experiment")

    SenLMoveToMMAction = QAction("Move to MM")
    SenLMoveToPosAction = QAction("Move to Pos")
    SenLMoveToPercentAction = QAction("Move to %")
    SenLJogAction = QAction("Jog")
    SenLMapPosAction = QAction("Map position")
    SenLHomeAction = QAction("Home SEN")
    SenLSetHomeAction = QAction("Set Home Posisiton")

    SenRMoveToMMAction = QAction("Move to MM")
    SenRMoveToPosAction = QAction("Move to Pos")
    SenRMoveToPercentAction = QAction("Move to %")
    SenRJogAction = QAction("Jog")
    SenRMapPosAction = QAction("Map position")
    SenRHomeAction = QAction("Home SEN")
    SenRSetHomeAction = QAction("Set Home Posisiton")

    SenGetConfigAction = QAction("Get Config")
    SenHomeBothAction = QAction("Home both ports")

    _instance = None

    LOG_FMT_STR = f"[Menubar] - %s"

    @classmethod
    def get_instance(cls, parent=None):
        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)

        self._m_client = MqttClient.get_instance()

        app_menu = self.addMenu("App")
        exp_menu = self.addMenu("Experiment")
        sen_menu = self.addMenu("SEN")

        mqtt_submenu = app_menu.addMenu("Mqtt")
        app_menu.addAction(MenuBar.CloseAppAction)

        mqtt_submenu.addAction(MenuBar.ConnectMqttAction)
        mqtt_submenu.addAction(MenuBar.DisconnectMqttAction)

        exp_menu.addAction(MenuBar.StartExpAction)
        exp_menu.addAction(MenuBar.RenameExpAction)
        exp_menu.addAction(MenuBar.StopExpAction)

        sen_menu.addAction(MenuBar.SenGetConfigAction)
        sen_menu.addAction(MenuBar.SenHomeBothAction)

        left_port_submenu = sen_menu.addMenu("Left Port")
        left_port_submenu.addAction(MenuBar.SenLMapPosAction)
        left_port_submenu.addAction(MenuBar.SenLMoveToMMAction)
        left_port_submenu.addAction(MenuBar.SenLMoveToPosAction)
        left_port_submenu.addAction(MenuBar.SenLJogAction)
        left_port_submenu.addAction(MenuBar.SenLMoveToPercentAction)
        left_port_submenu.addAction(MenuBar.SenLHomeAction)
        left_port_submenu.addAction(MenuBar.SenLSetHomeAction)

        right_port_submenu = sen_menu.addMenu("Right Port")
        right_port_submenu.addAction(MenuBar.SenRMapPosAction)
        right_port_submenu.addAction(MenuBar.SenRMoveToMMAction)
        right_port_submenu.addAction(MenuBar.SenRMoveToPosAction)
        right_port_submenu.addAction(MenuBar.SenRJogAction)
        right_port_submenu.addAction(MenuBar.SenRMoveToPercentAction)
        right_port_submenu.addAction(MenuBar.SenRHomeAction)

        if parent is not None:
            self.CloseAppAction.triggered.connect(parent.close)

        MenuBar.ConnectMqttAction.triggered.connect(self._m_client.ConnectBroker)
        MenuBar.DisconnectMqttAction.triggered.connect(self._m_client.DisconnectBroker)

        MenuBar.StartExpAction.triggered.connect(self._m_client.StartExp)
        MenuBar.StopExpAction.triggered.connect(self._m_client.StopExp)
        MenuBar.RenameExpAction.triggered.connect(self._m_client.RenameExp)

        MenuBar.SenLMoveToPosAction.triggered.connect(self.SenLMoveToPosDialog)
        MenuBar.SenRMoveToPosAction.triggered.connect(self.SenRMoveToPosDialog)
        MenuBar.SenLMoveToMMAction.triggered.connect(self.SenLMoveToMMDialog)
        MenuBar.SenRMoveToMMAction.triggered.connect(self.SenRMoveToMMDialog)
        MenuBar.SenLMoveToPercentAction.triggered.connect(self.SenLMoveToPercentDialog)
        MenuBar.SenRMoveToPercentAction.triggered.connect(self.SenRMoveToPercentDialog)

        MenuBar.SenLSetHomeAction.triggered.connect(self._m_client.SenSetLHome)
        MenuBar.SenRSetHomeAction.triggered.connect(self._m_client.SeNSetRHome)




    @pyqtSlot()
    def SenLMoveToPosDialog(self):
        value, ok = QInputDialog.getInt(self, "Set Left SEN Pos", "Pos:", step=1)

        if ok and value >= 0:
            self._m_client.SenLMoveToPos(value)
        else:
            logging.warning(MenuBar.LOG_FMT_STR, "User cancelled or Value was None")

    @pyqtSlot()
    def SenRMoveToPosDialog(self):
        value, ok = QInputDialog.getInt(self, "Set Right SEN Pos", "Pos:", step=1)

        if ok and value >= 0:
            self._m_client.SenRMoveToPos(value)
        else:
            logging.warning(MenuBar.LOG_FMT_STR, "User cancelled or Value was None")

    @pyqtSlot()
    def SenLMoveToMMDialog(self):
        value, ok = QInputDialog.getDouble(self, "Set Left SEN MM", "MM:")

        if ok and value >= 0:
            self._m_client.SenLMoveToMM(value)
        else:
            logging.warning(MenuBar.LOG_FMT_STR, "User cancelled or Value was None")

    @pyqtSlot()
    def SenRMoveToMMDialog(self):
        value, ok = QInputDialog.getDouble(self, "Set Right SEN MM", "MM:")

        if ok and value >= 0:
            self._m_client.SenRMoveToMM(value)
        else:
            logging.warning(MenuBar.LOG_FMT_STR, "User cancelled or Value was None")

    @pyqtSlot()
    def SenLMoveToPercentDialog(self):
        value, ok = QInputDialog.getInt(self, "Set Left SEN Percent", "Percent:", step=1)

        if ok and value >= 0:
            self._m_client.SenLMovePercent(value)
        else:
            logging.warning(MenuBar.LOG_FMT_STR, "User cancelled or Value was None")

    @pyqtSlot()
    def SenRMoveToPercentDialog(self):
        value, ok = QInputDialog.getInt(self, "Set Right SEN Percent", "Percent:", step=1)

        if ok and value >= 0:
            self._m_client.SenRMovePercent(value)
        else:
            logging.warning(MenuBar.LOG_FMT_STR, "User cancelled or Value was None")

