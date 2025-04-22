from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from Transform import Size
from custom_qt_objects import *
from Mqtt import * 

class QAlarmWidget(QWidget):

    def __init__(self, alarm_name_1:str="alarm1", alarm_name_2:str="alarm2", alarm_name_3:str="alarm3", alarm_name_4:str="alarm4", parent=None, **kargs):
        super().__init__(parent, **kargs)

        self.h_box = QHBoxLayout(self)
        self.mqtt = QMqttAlarms()

        alarm1 = AlarmLabel(alarm_name_1)
        alarm2 = AlarmLabel(alarm_name_2)
        alarm3 = AlarmLabel(alarm_name_3)
        alarm4 = AlarmLabel(alarm_name_4)

        self.mqtt.alarm_signal_1.connect(alarm1.set_state)
        self.mqtt.alarm_signal_2.connect(alarm2.set_state)
        self.mqtt.alarm_signal_3.connect(alarm3.set_state)
        self.mqtt.alarm_signal_4.connect(alarm4.set_state)

        self.h_box.addWidget(alarm1)
        self.h_box.addWidget(alarm2)
        self.h_box.addWidget(alarm3)
        self.h_box.addWidget(alarm4)
        
class QCustomGraphsWidget(QWidget):

    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)

        self.main_v_box = QVBoxLayout(self)
        self.top_h_box = QHBoxLayout()

        self.left_graph = Q2SensorsGraph(title="Left Mould (LL, LQ)", size=Size(300, 300))
        self.right_graph = Q2SensorsGraph(title="Right Mould (RQ, RR)", size=Size(300, 300))
        self.standing_wave_graph = Q2SensorsGraph(title="Stating Wave Height (LL-LQ) (RR-RQ)", size=Size(600, 300))

        self.top_h_box.addWidget(self.left_graph)
        self.top_h_box.addWidget(self.right_graph)
        self.main_v_box.addLayout(self.top_h_box)
        self.main_v_box.addWidget(self.standing_wave_graph)


    @pyqtSlot()
    def update_plot(self, ll_value:float, lq_value:float, rq_value:float, rr_value:float):
        left_standing_wave = ll_value - lq_value
        right_standing_wave = rr_value - rq_value
        
        self.left_graph.update_plot(lq_value, ll_value)
        self.right_graph.update_plot(rq_value, rr_value)
        self.standing_wave_graph.update_plot(left_standing_wave, right_standing_wave)