
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStatusBar, QSizePolicy
from .Transform import Size
from .Mqtt.status_lights_mqtt import StatusLightsMqtt

class StatusWidget(QWidget):

    ELAPSED_SIZE = Size(200, 25)

    def __init__(self, status_bar:QStatusBar, alarm_name_1:str="alarm1", alarm_name_2:str="alarm2", alarm_name_3:str="alarm3", alarm_name_4:str="alarm4", log_name:str="Qt", host_name:str="localhost", host_port:int=1883, parent=None, **kargs):
        super().__init__(parent, **kargs)

        self.central_layout = QVBoxLayout(self)
        self.experiment_layout = QHBoxLayout()
        self.alarms_layout = QHBoxLayout()
        self.mqtt_client = StatusLightsMqtt(log_name, host_name, host_port)

        alarm1 = AlarmLabel(alarm_name_1)
        alarm2 = AlarmLabel(alarm_name_2)
        alarm3 = AlarmLabel(alarm_name_3)
        alarm4 = AlarmLabel(alarm_name_4)

        experiment_status = AlarmLabel("Experiment Status")
        self.experiment_timer = QLabel("Experiment Timer")

        self.experiment_timer.setMinimumSize(StatusWidget.ELAPSED_SIZE.w, StatusWidget.ELAPSED_SIZE.h)
        self.experiment_timer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mqtt_client.alarm_signal_1.connect(alarm1.set_state)
        self.mqtt_client.alarm_signal_2.connect(alarm2.set_state)
        self.mqtt_client.alarm_signal_3.connect(alarm3.set_state)
        self.mqtt_client.alarm_signal_4.connect(alarm4.set_state)

        self.mqtt_client.experiment_running.connect(experiment_status.set_state)
        self.mqtt_client.experiment_elapsed_time.connect(self.set_experiment_time)

        self.alarms_layout.addWidget(alarm1)
        self.alarms_layout.addWidget(alarm2)
        self.alarms_layout.addWidget(alarm3)
        self.alarms_layout.addWidget(alarm4)

        self.experiment_layout.addWidget(experiment_status)
        self.experiment_layout.addWidget(self.experiment_timer)

        self.central_layout.addLayout(self.experiment_layout)
        self.central_layout.addLayout(self.alarms_layout)

        # self.mqtt_alarms.mqtt_connect()

    @pyqtSlot(int)
    def set_experiment_time(self, elapsed_time:int):
        self.experiment_timer.setText(f"Elapsed Time: {elapsed_time} s")

class AlarmLabel(QLabel):

    DEFAULT_SIZE = Size(100, 25)

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
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
        color = QColor("lightgreen") if self.state else QColor("lightcoral")
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)