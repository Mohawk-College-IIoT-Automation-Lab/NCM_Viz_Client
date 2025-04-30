from PyQt5.QtWidgets import QStatusBar, QToolBar, QMainWindow, QAction, QMenuBar
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from .Mqtt.GenericMqtteLogger import GenericMQTT
import logging

class Actions(QObject):

    start_exp_signal = pyqtSignal()
    stop_exp_signal = pyqtSignal()
    reset_exp_signal = pyqtSignal()
    quit_signal = pyqtSignal()
    help_signal = pyqtSignal()
    settings_signal = pyqtSignal()
    sen_tuning_signal = pyqtSignal()
    sensor_tuning_signal = pyqtSignal()
    stopper_rod_tuning_signal = pyqtSignal()
    mould_fill_signal = pyqtSignal()
    mould_drain_signal = pyqtSignal()
    tundish_fill_signal = pyqtSignal()
    tundish_drain_signal = pyqtSignal()
    fill_all_signal = pyqtSignal()
    drain_all_signal = pyqtSignal()
    stopper_rod_closed_signal = pyqtSignal()
    stopper_rod_open_signal = pyqtSignal()
    sen_full_open_signal = pyqtSignal()
    sen_full_closed_signal = pyqtSignal()

    def __init__(self, status_bar:QStatusBar, parent=None, log_name:str="Qt", host_name:str="localhost", host_port:int=1883):
        super().__init__(parent)
        self.status_bar = status_bar
        self.mqtt_client = GenericMQTT(log_name, host_name, host_port)
        logging.debug("Creating M_ActionsSingleton object")

        # Create all the actions
        self.start_exp_action = QAction("Start Experiment", self)
        self.stop_exp_action = QAction("Stop Experiment", self)
        self.reset_exp_action = QAction("Reset Experiment", self)

        self.quit_action = QAction("Quit", self)
        self.help_action = QAction("Help", self)
        self.settings_action = QAction("Settings", self)

        self.sen_tuning_action = QAction("SEN Tuning", self)
        self.sensor_tuning_action = QAction("Sensor Tuning", self)
        self.stopper_rod_tuning_action = QAction("Stopper Rod Tuning", self)

        self.mould_fill_action = QAction("Mould Fill", self)
        self.mould_drain_action = QAction("Mould Drain", self)
        self.tundish_fill_action = QAction("Tundish Fill", self)
        self.tundish_drain_action = QAction("Tundish Drain", self)
        self.fill_all_action = QAction("Fill All", self)
        self.drain_all_action = QAction("Drain All", self)

        self.stopper_rod_closed_action = QAction("Stopper Rod Closed", self)
        self.stopper_rod_open_action = QAction("Stopper Rod Open", self)

        self.sen_full_open_action = QAction("SEN Full Open", self)
        self.sen_full_closed_action = QAction("SEN Full Closed", self)

        # Connect actions to slots
        self.start_exp_action.triggered.connect(self.start_exp)
        self.stop_exp_action.triggered.connect(self.stop_exp)
        self.reset_exp_action.triggered.connect(self.reset_exp)

        self.quit_action.triggered.connect(self.quit)
        self.help_action.triggered.connect(self.help)
        self.settings_action.triggered.connect(self.settings)

        self.sen_tuning_action.triggered.connect(self.sen_tuning)
        self.sensor_tuning_action.triggered.connect(self.sensor_tuning)
        self.stopper_rod_tuning_action.triggered.connect(self.stopper_rod_tuning)

        self.mould_fill_action.triggered.connect(self.mould_fill)
        self.mould_drain_action.triggered.connect(self.mould_drain) 
        self.tundish_fill_action.triggered.connect(self.tundish_fill)
        self.tundish_drain_action.triggered.connect(self.tundish_drain)
        self.fill_all_action.triggered.connect(self.fill_all)
        self.drain_all_action.triggered.connect(self.drain_all)

        self.stopper_rod_closed_action.triggered.connect(self.stopper_rod_closed)
        self.stopper_rod_open_action.triggered.connect(self.stopper_rod_open)
        self.sen_full_open_action.triggered.connect(self.sen_full_open)
        self.sen_full_closed_action.triggered.connect(self.sen_full_closed)

        # self.mqtt_connect()

    def status_and_log(self, message:str, duration:int=1000):
        logging.info(message)
        self.status_bar.showMessage(message, duration)

    @pyqtSlot()
    def start_exp(self):
        self.start_exp_signal.emit()
        self.status_and_log("[QT][Action] Start Experiment")
        self.mqtt_client.publish("NCM/Experiment_Control", "Start")
    
    @pyqtSlot()
    def stop_exp(self):
        self.stop_exp_signal.emit()
        self.status_and_log("[QT][Action] Stop Experiment")
        self.mqtt_client.publish("NCM/Experiment_Control", "Stop")

    @pyqtSlot()
    def reset_exp(self):
        self.reset_exp_signal.emit()
        self.status_and_log("[QT][Action] Reset Experiment")
        self.mqtt_client.publish("NCM/Experiment_Control", "Reset")

    @pyqtSlot()
    def quit(self):
        self.status_and_log("[QT][Action] Quit")
        self.mqtt_client.publish("NCM/App_Status", "Quit")

    @pyqtSlot()
    def help(self):
        self.status_and_log("[QT][Action] Help")

    @pyqtSlot()
    def settings(self):
        self.status_and_log("[QT][Action] Settings")

    @pyqtSlot()
    def sen_tuning(self):
        self.status_and_log("[QT][Action] SEN Tuning")

    @pyqtSlot()
    def sensor_tuning(self):
        self.status_and_log("[QT][Action] Sensor Tuning")

    @pyqtSlot()
    def stopper_rod_tuning(self):
        self.status_and_log("[QT][Action] Stopper Rod Tuning")

    @pyqtSlot()
    def mould_fill(self):
        self.status_and_log("[QT][Action] Mould Fill")

    @pyqtSlot()
    def mould_drain(self):
        self.status_and_log("[QT][Action] Mould Drain")

    @pyqtSlot()
    def tundish_fill(self):
        self.status_and_log("[QT][Action] Tundish Fill")

    @pyqtSlot()  
    def tundish_drain(self):
        self.status_and_log("[QT][Action] Tundish Drain")
    
    @pyqtSlot()
    def fill_all(self):
        self.status_and_log("[QT][Action] Fill All")

    @pyqtSlot()
    def drain_all(self):
        self.status_and_log("[QT][Action] Drain All")

    @pyqtSlot()
    def stopper_rod_closed(self):
        self.status_and_log("[QT][Action] Stopper Rod Closed")

    @pyqtSlot()
    def stopper_rod_open(self):
        self.status_and_log("[QT][Action] Stopper Rod Open")

    @pyqtSlot()
    def sen_full_open(self):
        self.status_and_log("[QT][Action] SEN Full Open")

    @pyqtSlot()
    def sen_full_closed(self):
        self.status_and_log("[QT][Action] SEN Full Closed")


        



