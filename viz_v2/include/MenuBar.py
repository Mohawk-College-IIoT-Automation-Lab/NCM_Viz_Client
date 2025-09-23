from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QAction, QMenuBar

from .Mqtt import MqttClient


class MenuBar(QMenuBar):

    CloseAppAction = QAction("Close App")
    ConnectMqttAction = QAction("Conect Mqtt")
    DisconnectMqttAction = QAction("Disconnect Mqtt")

    StartExpAction = QAction("Start Experiment")
    RenameExpAction = QAction("Rename Experiment")
    StopExpAction = QAction("Stop Experiment")

    SenMoveToMMAction = QAction("Move to MM")
    SenMoveToPosAction = QAction("Move to Pos")
    SenMoveToIdxAction = QAction("Move to Index")
    SenJogAction = QAction("Jog")
    SenSetConfigAction = QAction("Set config")
    SenGetConfigAction = QAction("Get Config")

    _instance = None

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
        sen_menu.addAction(MenuBar.SenSetConfigAction)

        sen_cmd_submenu = sen_menu.addMenu("Move to")
        sen_cmd_submenu.addAction(MenuBar.SenMoveToMMAction)
        sen_cmd_submenu.addAction(MenuBar.SenMoveToPosAction)
        sen_cmd_submenu.addAction(MenuBar.SenMoveToIdxAction)
        sen_cmd_submenu.addAction(MenuBar.SenJogAction)
        
        if parent is not None:
            self.CloseAppAction.triggered.connect(parent.close)

        MenuBar.ConnectMqttAction.triggered.connect(self._m_client.ConnectBroker)
        MenuBar.DisconnectMqttAction.triggered.connect(self._m_client.DisconnectBroker)
       
        MenuBar.StartExpAction.triggered.connect(self._m_client.StartExp)
        MenuBar.StopExpAction.triggered.connect(self._m_client.StopExp)
        MenuBar.RenameExpAction.triggered.connect(self._m_client.RenameExp)


