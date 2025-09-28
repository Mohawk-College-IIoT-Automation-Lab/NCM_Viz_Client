import logging
from PyQt5.QtCore import pyqtSlot
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
    SenLMoveToIdxAction = QAction("Move to Index")
    SenLJogAction = QAction("Jog")
    SenLMapPosAction = QAction("Map position")

    SenRMoveToMMAction = QAction("Move to MM")
    SenRMoveToPosAction = QAction("Move to Pos")
    SenRMoveToIdxAction = QAction("Move to Index")
    SenRJogAction = QAction("Jog")
    SenRMapPosAction = QAction("Map position")

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
        left_port_submenu.addAction(MenuBar.SenLMoveToIdxAction)
        left_port_submenu.addAction(MenuBar.SenLJogAction)

        right_port_submenu = sen_menu.addMenu("Right Port")
        right_port_submenu.addAction(MenuBar.SenRMapPosAction)
        right_port_submenu.addAction(MenuBar.SenRMoveToMMAction)
        right_port_submenu.addAction(MenuBar.SenRMoveToPosAction)
        right_port_submenu.addAction(MenuBar.SenRMoveToIdxAction)
        right_port_submenu.addAction(MenuBar.SenRJogAction)
        
        if parent is not None:
            self.CloseAppAction.triggered.connect(parent.close)

        MenuBar.ConnectMqttAction.triggered.connect(self._m_client.ConnectBroker)
        MenuBar.DisconnectMqttAction.triggered.connect(self._m_client.DisconnectBroker)
       
        MenuBar.StartExpAction.triggered.connect(self._m_client.StartExp)
        MenuBar.StopExpAction.triggered.connect(self._m_client.StopExp)
        MenuBar.RenameExpAction.triggered.connect(self._m_client.RenameExp)

        MenuBar.SenLMoveToPosAction.triggered.connect(self.SenLMoveToPosDialog)


    @pyqtSlot()
    def SenLMoveToPosDialog(self):
        value, ok = QInputDialog.getInt(self, "Set Left SEN Pos", "Pos:", value = 0, min=0, max=70000, step=1)

        if ok and value:
            self._m_client.SenLMoveToPos(value)
        else:
            logging.warning(MenuBar.LOG_FMT_STR, "User cancelled or Value was None")

    @pyqtSlot()
    def SenRMoveToPosDialog(self):
        value, ok = QInputDialog.getInt(self, "Set Right SEN Pos", "Pos:", value = 0, min=0, max=70000, step=1)

        if ok and value:
            self._m_client.SenRMoveToPos(value)
        else:
            logging.warning(MenuBar.LOG_FMT_STR, "User cancelled or Value was None")





