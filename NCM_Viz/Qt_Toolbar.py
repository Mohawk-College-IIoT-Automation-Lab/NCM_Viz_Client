from PyQt5.QtWidgets import QToolBar, QMainWindow, QMenuBar, QStatusBar
from .Mqtt.actions_mqtt import Actions
from Constants.configs import LoggerConfig

class M_QToolBar(QToolBar):
    def __init__(self, title:str, parent:QMainWindow, status_bar:QStatusBar, logger_confgi:LoggerConfig):
        super().__init__(title, parent)
        self.setMovable(False)
        self.setFloatable(False)

        actions_inst = Actions.get_instance()


class M_QMenuBar(QMenuBar):
    def __init__(self, title:str, parent:QMainWindow):
        super().__init__(parent)