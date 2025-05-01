
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStatusBar
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from .Mqtt.sensors_mqtt import SensorsMQTT
from .QT_Custom_Graphs import Q2SensorsGraph

from Constants.configs import LoggerConfig, MQTTConfig, SensorsConfig


class SensorGraphWidget(QWidget):

    def __init__(self, status_bar:QStatusBar, logger_config:LoggerConfig = LoggerConfig, parent=None, **kargs):
        super().__init__(parent, **kargs)

        main_h_box = QHBoxLayout(self)
        left_v_box = QVBoxLayout()
        right_v_box = QVBoxLayout()
        left_h_box = QHBoxLayout()

        self.usd_ll_lq_graph = Q2SensorsGraph(title=SensorsConfig.usd_left_title)
        self.usd_rq_rr_graph = Q2SensorsGraph(title=SensorsConfig.usd_right_title)
        self.standing_wave_graph = Q2SensorsGraph(title=SensorsConfig.standing_wave_title)

        self.an_ll_lq_graph = Q2SensorsGraph(title=SensorsConfig.anm_left_title)
        self.an_rq_rr_graph = Q2SensorsGraph(title=SensorsConfig.anm_right_title)

        left_h_box.addWidget(self.usd_ll_lq_graph)
        left_h_box.addWidget(self.usd_rq_rr_graph)

        left_v_box.addWidget(self.standing_wave_graph)
        left_v_box.addLayout(left_h_box)

        right_v_box.addWidget(self.an_ll_lq_graph)
        right_v_box.addWidget(self.an_rq_rr_graph)
        
        main_h_box.addLayout(left_v_box)
        main_h_box.addLayout(right_v_box)

        self.setLayout(main_h_box)

        self.mqtt_client = SensorsMQTT.get_instance(logger_config=logger_config)
        self.mqtt_client.distance_data_ready.connect(self.update_usd_plot)
        self.mqtt_client.anemometer_data_ready.connect(self.update_an_plot)
        

    @pyqtSlot(float, float, float, float)
    def update_usd_plot(self, ll_value:float, lq_value:float, rq_value:float, rr_value:float):
        left_standing_wave = ll_value - lq_value
        right_standing_wave = rr_value - rq_value
        
        self.usd_ll_lq_graph.update_plot(lq_value, ll_value)
        self.usd_rq_rr_graph.update_plot(rq_value, rr_value)
        self.standing_wave_graph.update_plot(left_standing_wave, right_standing_wave)

    @pyqtSlot(float, float, float, float)
    def update_an_plot(self, ll_value:float, lq_value:float, rq_value:float, rr_value:float):
        self.an_ll_lq_graph.update_plot(lq_value, ll_value)
        self.an_rq_rr_graph.update_plot(rq_value, rr_value)