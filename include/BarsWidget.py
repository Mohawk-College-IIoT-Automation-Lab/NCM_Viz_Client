from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

import logging

from .graphs.Graphs import DualPointPlotWidget
from .DataStructures import SensorData, MCUData
from .Mqtt import MqttClient
from .MenuBar import MenuBar


class BarsWidget(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)

        _m_client = MqttClient.get_instance()

        """ A central V box will hold 1 h box and one plot below
            - The left most hbox will be LL signed velocity
            - The middle left hbox will be LQ signed velocity
            - The middle right hbox will be RQ signed velocity
            - The right most hbox will be RR signed velocity
            - The bottom plot will be bar set of all pressures
        """

        center_v_box = QVBoxLayout(self)
        top_h_box = QHBoxLayout()

        self._l_wl_graph = DualPointPlotWidget(title="Left Waterlevel", y_label="MM", d1_label="LL", d2_label="LQ")
        self._r_wl_graph = DualPointPlotWidget(title="Right Waterlevel", y_label="MM", d1_label="RQ", d2_label="RR")
        self._l_v_graph = DualPointPlotWidget(title="Left Velocity", y_label="m/s", d1_label="LL", d2_label="LQ")
        self._r_v_graph = DualPointPlotWidget(title="Right Velocity", y_label="m/s", d1_label="RQ", d2_label="RR")
        self._pressure_barset = DualPointPlotWidget(title="Standing Wave", y_label="MM", d1_label="Left", d2_label="Right", height=200)

        top_h_box.addWidget(self._l_wl_graph, 0, 0)
        top_h_box.addWidget(self._r_wl_graph, 0, 1)
        top_h_box.addWidget(self._l_v_graph, 1, 0)
        top_h_box.addWidget(self._r_v_graph, 1, 1)

        center_v_box.addLayout(top_h_box)
        center_v_box.addWidget(self._pressure_barset)
        self.setLayout(center_v_box)

        _m_client.McuDataSignal.connect(self.UpdateBars)
        MenuBar.StartExpAction.triggered.connect(self.ClearPlots)

    @pyqtSlot()
    def ClearPlots(self):
        self._l_v_graph.ClearPlot()
        self._l_v_graph.ClearPlot()
        self._pressure_barset.ClearPlot()

    @pyqtSlot(MCUData)
    def UpdatePlots(self, data: SensorData):
        self._l_wl_graph.UpdateD1(data.Ultra_Sonic_Distance.LL)
        self._l_wl_graph.UpdateD2(data.Ultra_Sonic_Distance.LQ)

        self._r_wl_graph.UpdateD1(data.Ultra_Sonic_Distance.RQ)
        self._r_wl_graph.UpdateD2(data.Ultra_Sonic_Distance.RR)

        self._l_v_graph.UpdateD1(data.Anemometer.LL)
        self._l_v_graph.UpdateD2(data.Anemometer.LQ)

        self._r_v_graph.UpdateD1(data.Anemometer.RQ)
        self._r_v_graph.UpdateD2(data.Anemometer.RR)

        self._pressure_barset.UpdateD1(data.Standing_Wave.Left)
        self._pressure_barset.UpdateD2(data.Standing_Wave.Right)






