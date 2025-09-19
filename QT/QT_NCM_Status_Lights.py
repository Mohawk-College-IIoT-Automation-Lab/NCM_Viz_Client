
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStatusBar, QSizePolicy
from .Transform import Size
from Mqtt.status_lights_mqtt import StatusLightsMqtt
from Constants.configs import LoggerConfig, StatusLightsMqttConfig
import logging

class StatusWidget(QWidget):

    ELAPSED_SIZE = Size(200, 25)

    def __init__(self, status_bar:QStatusBar, logger_config:LoggerConfig, parent=None, **kargs):
        super().__init__(parent, **kargs)
        self.central_layout = QVBoxLayout(self)
        self.experiment_layout = QHBoxLayout()
        self.alarms_layout = QHBoxLayout()
        self.mqtt_client = StatusLightsMqtt.get_instance(logger_config=logger_config)

        self.alarm_labels = []

        for an in StatusLightsMqttConfig.alarm_topics:
            self.alarm_labels.append(AlarmLabel(an))

        experiment_status = AlarmLabel("Experiment Status")
        self.experiment_timer = QLabel("Experiment Timer")

        self.experiment_timer.setMinimumSize(StatusWidget.ELAPSED_SIZE.w, StatusWidget.ELAPSED_SIZE.h)
        self.experiment_timer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mqtt_client.alarm_signal.connect(self.alarm_status_set)
        self.mqtt_client.experiment_running.connect(experiment_status.set_state)
        self.mqtt_client.experiment_elapsed_time.connect(self.set_experiment_time)

        for a in self.alarm_labels:
            self.alarms_layout.addWidget(a)
            
        self.experiment_layout.addWidget(experiment_status)
        self.experiment_layout.addWidget(self.experiment_timer)

        self.central_layout.addLayout(self.experiment_layout)
        self.central_layout.addLayout(self.alarms_layout)

    @pyqtSlot(str, bool)
    def alarm_status_set(self, alarm_name:str, status:bool):
        for al in self.alarm_labels:
            if alarm_name in al.name:
                print(status)
                al.set_state(status)
                logging.debug(f"[Qt][Status Lights] Setting Alarms: {alarm_name}")
                return

    @pyqtSlot(float)
    def set_experiment_time(self, elapsed_time:float):
        self.experiment_timer.setText(f"Elapsed Time: {elapsed_time:.3f} s")

class AlarmLabel(QLabel):

    DEFAULT_SIZE = Size(100, 25)
    ON_COLOUR = QColor("lightgreen")
    OFF_COLOUR = QColor("lightcoral")

    def __init__(self, name="", parent=None):
        super().__init__(name, parent)
        self._name = name
        self.setAutoFillBackground(True)
        self.state = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_style()
        self.setMinimumSize(AlarmLabel.DEFAULT_SIZE.w, AlarmLabel.DEFAULT_SIZE.h)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    @pyqtSlot(bool)
    def set_state(self, state:bool):
        self.state = state
        self.update_style()
    
    def update_style(self):
        palette = self.palette()
        if self.state:
            palette.setColor(QPalette.Window, AlarmLabel.ON_COLOUR)
        else:
            palette.setColor(QPalette.Window, AlarmLabel.OFF_COLOUR)
        self.setPalette(palette)

    @property
    def name(self):
        return self._name
