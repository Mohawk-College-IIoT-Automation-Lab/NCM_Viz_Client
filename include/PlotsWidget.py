from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

import logging
import time

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

        # time_axis: x = the message Timestamp, shown as clock time
        self._l_wl_graph = DualPointPlotWidget(title="Left Waterlevel", y_label="MM", x_label="time", d1_label="LL", d2_label="LQ", time_axis=True)
        self._r_wl_graph = DualPointPlotWidget(title="Right Waterlevel", y_label="MM", x_label="time", d1_label="RQ", d2_label="RR", time_axis=True)
        self._l_v_graph = DualPointPlotWidget(title="Left Velocity", y_label="m/s", x_label="time", d1_label="LL", d2_label="LQ", time_axis=True)
        self._r_v_graph = DualPointPlotWidget(title="Right Velocity", y_label="m/s", x_label="time", d1_label="RQ", d2_label="RR", time_axis=True)
        self._standing_graph = DualPointPlotWidget(title="Standing Wave", y_label="MM", x_label="time", d1_label="Left", d2_label="Right", height=200, time_axis=True)

        top_g_box.addWidget(self._l_wl_graph, 0, 0)
        top_g_box.addWidget(self._r_wl_graph, 0, 1)
        top_g_box.addWidget(self._l_v_graph, 1, 0)
        top_g_box.addWidget(self._r_v_graph, 1, 1)

        center_v_box.addLayout(top_g_box)
        center_v_box.addWidget(self._standing_graph)
        self.setLayout(center_v_box)

        _m_client.DaqDataSignal.connect(self.UpdatePlots)
        MenuBar.PrepareExpAction.triggered.connect(self.ClearPlots)

    @pyqtSlot()
    def ClearPlots(self):
        self._l_wl_graph.ClearPlot()
        self._r_wl_graph.ClearPlot()
        self._l_v_graph.ClearPlot()
        self._r_v_graph.ClearPlot()
        self._standing_graph.ClearPlot()

    @pyqtSlot(SensorData)
    def UpdatePlots(self, data: SensorData):
        # x = the batch's timestamp in Unix seconds (shown as clock time).
        # Publishers without a Timestamp fall back to the arrival time.
        t = data.Timestamp / 1e6 if data.Timestamp is not None else time.time()

        self._l_wl_graph.UpdateD1At(t, data.Ultra_Sonic_Distance.LL)
        self._l_wl_graph.UpdateD2At(t, data.Ultra_Sonic_Distance.LQ)

        self._r_wl_graph.UpdateD1At(t, data.Ultra_Sonic_Distance.RQ)
        self._r_wl_graph.UpdateD2At(t, data.Ultra_Sonic_Distance.RR)

        self._l_v_graph.UpdateD1At(t, data.Anemometer.LL)
        self._l_v_graph.UpdateD2At(t, data.Anemometer.LQ)

        self._r_v_graph.UpdateD1At(t, data.Anemometer.RQ)
        self._r_v_graph.UpdateD2At(t, data.Anemometer.RR)

        self._standing_graph.UpdateD1At(t, data.Standing_Wave.Left)
        self._standing_graph.UpdateD2At(t, data.Standing_Wave.Right)






