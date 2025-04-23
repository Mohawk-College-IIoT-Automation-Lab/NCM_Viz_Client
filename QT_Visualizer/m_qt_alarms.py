from Transform import Size
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from m_qobject import *

class QMqttAlarms(M_QObject):

    alarm_signal_1 = pyqtSignal(bool)
    alarm_signal_2 = pyqtSignal(bool)
    alarm_signal_3 = pyqtSignal(bool)
    alarm_signal_4 = pyqtSignal(bool)

    def __init__(self, host_address:str="localhost", host_port:int=1883, parent=None):
        super().__init__(False, host_address, host_port, parent)

        self.alarm_topic = "NCM/Alarm/#" # all alarm topics

        self.mqtt_client.message_callback_add(self.alarm_topic, self.mqtt_alarm_callback)
        self.mqtt_client.subscribe(self.alarm_topic)
    
    def mqtt_alarm_callback(self, client:Client, userdata, message:MQTTMessage):
        if message.topic == "Alarm1":
            self.alarm_signal_1.emit(bool(message.payload))
            self.emit_and_log(f"[MQTT][Alarm1] Received data: {message.payload}")

        elif message.topic == "Alarm2":
            self.alarm_signal_2.emit(bool(message.payload))
            self.emit_and_log(f"[MQTT][Alarm2] Received data: {message.payload}")

        elif message.topic == "Alarm3":
            self.alarm_signal_3.emit(bool(message.payload))
            self.emit_and_log(f"[MQTT][Alarm3] Received data: {message.payload}")

        elif message.topic == "Alarm4":
            self.alarm_signal_4.emit(bool(message.payload))
            self.emit_and_log(f"[MQTT][Alarm4] Received data: {message.payload}")
            
        else:
            self._mqtt_default_callback(client, userdata, message)


class QAlarmWidget(QWidget):

    def __init__(self, alarm_name_1:str="alarm1", alarm_name_2:str="alarm2", alarm_name_3:str="alarm3", alarm_name_4:str="alarm4", host_name:str="localhost", host_port:int=1883, parent=None, **kargs):
        super().__init__(parent, **kargs)

        self.central_layout = QHBoxLayout(self)
        self.alarm_m_qobject = QMqttAlarms(host_name, host_port)

        alarm1 = AlarmLabel(alarm_name_1)
        alarm2 = AlarmLabel(alarm_name_2)
        alarm3 = AlarmLabel(alarm_name_3)
        alarm4 = AlarmLabel(alarm_name_4)

        self.alarm_m_qobject.alarm_signal_1.connect(alarm1.set_state)
        self.alarm_m_qobject.alarm_signal_2.connect(alarm2.set_state)
        self.alarm_m_qobject.alarm_signal_3.connect(alarm3.set_state)
        self.alarm_m_qobject.alarm_signal_4.connect(alarm4.set_state)

        self.central_layout.addWidget(alarm1)
        self.central_layout.addWidget(alarm2)
        self.central_layout.addWidget(alarm3)
        self.central_layout.addWidget(alarm4)

        # self.mqtt_alarms.mqtt_connect()

class AlarmLabel(QLabel):

    DEFAULT_SIZE = Size(100, 25)

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAutoFillBackground(True)
        self.state = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_style()
        self.setFixedHeight(AlarmLabel.DEFAULT_SIZE.h)

    @pyqtSlot(bool)
    def set_state(self, state:bool):
        self.state = state
        self.update_style()
    
    def update_style(self):
        palette = self.palette()
        color = QColor("lightgreen") if self.state else QColor("lightcoral")
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)