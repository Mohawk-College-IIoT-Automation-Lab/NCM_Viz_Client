
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStatusBar
from PyQt5.QtCore import pyqtSlot

from Mqtt.sensors_mqtt import SensorsMQTT
from .QT_Custom_Graphs import Q2SensorsGraph
from .QT_Constants import SensorQTConfig

from Constants.base_models import SensorData
from Constants.configs import LoggerConfig



class SensorGraphWidget(QWidget):

    def __init__(self, logger_config:LoggerConfig, parent=None, **kargs):
        super().__init__(parent, **kargs)

        main_h_box = QHBoxLayout(self)
        left_v_box = QVBoxLayout()
        right_v_box = QVBoxLayout()
        left_h_box = QHBoxLayout()

        # color_1 => LQ => pink [0]
        # color_2 => LL => cyan [1]
        self.usd_left_graph = Q2SensorsGraph(title=SensorQTConfig.usd_left_title, color_1=SensorQTConfig.colors[0][0], color_2=SensorQTConfig.colors[0][1])

        # color_1 => RQ => orange [2]
        # color_2 => RR => brown [3]
        self.usd_right_graph = Q2SensorsGraph(title=SensorQTConfig.usd_right_title, color_1=SensorQTConfig.colors[0][2], color_2=SensorQTConfig.colors[0][3])
        
        self.standing_wave_graph = Q2SensorsGraph(title=SensorQTConfig.standing_wave_title, color_1=SensorQTConfig.colors[1][0], color_2=SensorQTConfig.colors[1][1])

        self.anm_left_graph = Q2SensorsGraph(title=SensorQTConfig.anm_left_title, color_1=SensorQTConfig.colors[0][0], color_2=SensorQTConfig.colors[0][1], label="Velocity", units="m/s")
        self.anm_right_graph = Q2SensorsGraph(title=SensorQTConfig.anm_right_title, color_1=SensorQTConfig.colors[0][2], color_2=SensorQTConfig.colors[0][3], label="Velocity", units="m/s")

        self.usd_left_graph.setYRange(0, 300)
        self.usd_right_graph.setYRange(0, 300)
        self.anm_left_graph.setYRange(0, 1)
        self.anm_right_graph.setYRange(0, 1)
        
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
        self.mqtt_client.sensor_data_signal.connect(self.update_plots)
        self.mqtt_client.clear_plots_signal.connect(self.clear_plots)
    
    @pyqtSlot()
    def clear_plots(self):
        self.usd_left_graph.clear_plot()
        self.usd_right_graph.clear_plot()
        self.anm_left_graph.clear_plot()
        self.anm_right_graph.clear_plot()
        self.standing_wave_graph.clear_plot()

    @pyqtSlot(SensorData):
    def update_plots(self, sensor_data: SensorData):
        self.usd_left_graph.update_plot(sensor_data.Ultra_Sonic_Distance.LQ, sensor_data.Ultra_Sonic_Distance.LL)
        self.usd_right_graph.update_plot(sensor_data.Ultra_Sonic_Distance.RQ, sensor_data.Ultra_Sonic_Distance.RR)
        self.anm_left_graph.update_plot(sensor_data.Anemometer.LQ, sensor_data.Anemometer.LL)
        self.anm_right_graph.update_plot(sensor_data.Anemometer.RQ, sensor_data.Anemometer.RR)

        self.standing_wave_graph.update_plot(sensor_data.Standing_Wave.Left, sensor_data.Standing_Wave.Right)



