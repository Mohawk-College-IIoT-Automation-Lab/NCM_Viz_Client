from PyQt5.QtWidgets import QMenuBar, QStatusBar
from .Mqtt.actions_mqtt import ActionsMQTT
from Constants.configs import LoggerConfig

class M_QMenuBar(QMenuBar):
    def __init__(self, status_bar:QStatusBar, logger_config:LoggerConfig, parent = None):
        super().__init__(parent)

        actions_inst = ActionsMQTT.get_instance(status_bar=status_bar, logger_config=logger_config)

        file_menu = self.addMenu("File")
        exp_menu = self.addMenu("Experiment")
        mould_menu = self.addMenu("Mould")

        file_menu.addAction(actions_inst.help_action)

        exp_menu.addAction(actions_inst.start_exp_action)
        exp_menu.addAction(actions_inst.stop_exp_action)
        exp_menu.addAction(actions_inst.rename_exp_action)
