from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

import logging

from .graphs.Graphs import DualPointPlotWidget
from .DataStructures import SensorData
from .Mqtt import MqttClient
from .MenuBar import MenuBar


class PlotsWidget(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)

        _m_client = MqttClient.get_instance()

        """ A central H box will hold 2 v boxs and one plot below
            - The left most vbox will be water level
            - The right most vbox will be velocity 
            - The bottom plot will be standing wave
        """

        center_v_box = QVBoxLayout(self)
        top_g_box = QGridLayout()

        self._l_wl_graph = DualPointPlotWidget(title="Left Waterlevel", y_label="MM", d1_label="LL", d2_label="LQ")
        self._r_wl_graph = DualPointPlotWidget(title="Right Waterlevel", y_label="MM", d1_label="RQ", d2_label="RR")
        self._l_v_graph = DualPointPlotWidget(title="Left Velocity", y_label="m/s", d1_label="LL", d2_label="LQ")
        self._r_v_graph = DualPointPlotWidget(title="Right Velocity", y_label="m/s", d1_label="RQ", d2_label="RR")
        self._standing_graph = DualPointPlotWidget(title="Standing Wave", y_label="MM", d1_label="Left", d2_label="Right")

        top_g_box.addWidget(self._l_wl_graph, 0, 0)
        top_g_box.addWidget(self._r_wl_graph, 0, 1)
        top_g_box.addWidget(self._l_v_graph, 1, 0)
        top_g_box.addWidget(self._r_v_graph, 1, 1)

        center_v_box.addLayout(top_g_box)
        center_v_box.addWidget(self._standing_graph)
        self.setLayout(center_v_box)

        _m_client.DaqDataSignal.connect(self.UpdatePlots)
        MenuBar.StartExpAction.triggered.connect(self.ClearPlots)

    @pyqtSlot()
    def ClearPlots(self):
        self._l_wl_graph.ClearPlot()
        self._r_wl_graph.ClearPlot()
        self._l_v_graph.ClearPlot()
        self._l_v_graph.ClearPlot()
        self._standing_graph.ClearPlot()

    @pyqtSlot()
    def UpdatePlots(self, data: SensorData):
        self._l_wl_graph.UpdatePlot(data.Ultra_Sonic_Distance.LL, data.Ultra_Sonic_Distance.LQ)
        self._r_wl_graph.UpdatePlot(data.Ultra_Sonic_Distance.RQ, data.Ultra_Sonic_Distance.RR)

        self._l_v_graph.UpdatePlot(data.Anemometer.LL, data.Anemometer.LQ)
        self._r_v_graph.UpdatePlot(data.Anemometer.RQ, data.Anemometer.RR)

        self._standing_graph.UpdatePlot(data.Standing_Wave.Left, data.Standing_Wave.Right)






