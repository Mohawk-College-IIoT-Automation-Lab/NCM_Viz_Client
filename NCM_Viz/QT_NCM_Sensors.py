
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStatusBar
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from .Mqtt.sensors_mqtt import SensorsMQTT
from .QT_Custom_Graphs import Q2SensorsGraph

from Constants.configs import LoggerConfig, MQTTConfig, SensorsConfig, DAQConfig


class SensorGraphWidget(QWidget):

    def __init__(self, status_bar:QStatusBar, logger_config:LoggerConfig = LoggerConfig, parent=None, **kargs):
        super().__init__(parent, **kargs)

        main_h_box = QHBoxLayout(self)
        left_v_box = QVBoxLayout()
        right_v_box = QVBoxLayout()
        left_h_box = QHBoxLayout()

        self.usd_left_graph = Q2SensorsGraph(title=SensorsConfig.usd_left_title, color_1=SensorsConfig.colors[0][0], color_2=SensorsConfig.colors[0][1])
        self.usd_right_graph = Q2SensorsGraph(title=SensorsConfig.usd_right_title, color_1=SensorsConfig.colors[1][0], color_2=SensorsConfig.colors[1][1])
        self.standing_wave_graph = Q2SensorsGraph(title=SensorsConfig.standing_wave_title, color_1=SensorsConfig.colors[2][0], color_2=SensorsConfig.colors[2][1])

        self.anm_left_graph = Q2SensorsGraph(title=SensorsConfig.anm_left_title, color_1=SensorsConfig.colors[0][0], color_2=SensorsConfig.colors[0][1])
        self.anm_right_graph = Q2SensorsGraph(title=SensorsConfig.anm_right_title, color_1=SensorsConfig.colors[1][0], color_2=SensorsConfig.colors[1][1])

        self.usd_left_graph.setYRange(0, 900)
        self.usd_right_graph.setYRange(0, 900)
        self.anm_left_graph.setYRange(0, 5)
        self.anm_right_graph.setYRange(0, 5)
        
        left_h_box.addWidget(self.usd_left_graph)
        left_h_box.addWidget(self.usd_right_graph)

        left_v_box.addWidget(self.standing_wave_graph)
        left_v_box.addLayout(left_h_box)

        right_v_box.addWidget(self.anm_left_graph)
        right_v_box.addWidget(self.anm_right_graph)
        
        main_h_box.addLayout(left_v_box)
        main_h_box.addLayout(right_v_box)

        self.setLayout(main_h_box)

        self.mqtt_client = SensorsMQTT.get_instance(logger_config=logger_config)
        self.mqtt_client.distance_data_ready.connect(self.update_usd_plot)
        self.mqtt_client.anemometer_data_ready.connect(self.update_an_plot)
        self.mqtt_client.standing_wave_ready.connect(self.update_standing_plot)
        self.mqtt_client.clear_plots_signal.connect(self.clear_plots)
    
    @pyqtSlot()
    def clear_plots(self):
        self.usd_left_graph.clear_plot()
        self.usd_right_graph.clear_plot()
        self.anm_left_graph.clear_plot()
        self.anm_right_graph.clear_plot()
        self.standing_wave_graph.clear_plot()

    @pyqtSlot(float, float, float, float)
    def update_usd_plot(self, ll_value:float, lq_value:float, rq_value:float, rr_value:float):       
        self.usd_left_graph.update_plot(lq_value, ll_value)
        self.usd_right_graph.update_plot(rq_value, rr_value)

    @pyqtSlot(float, float)
    def update_standing_plot(self, left_value:float, right_value:float):
        self.standing_wave_graph.update_plot(left_value, right_value)

    @pyqtSlot(float, float, float, float)
    def update_an_plot(self, ll_value:float, lq_value:float, rq_value:float, rr_value:float):
        self.anm_left_graph.update_plot(lq_value, ll_value)
        self.anm_right_graph.update_plot(rq_value, rr_value)
