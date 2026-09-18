from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

import logging

from .graphs.Graphs import DualPointPlotWidget
from .DataStructures import MCUData, Location
from .Mqtt import MqttClient
from .MenuBar import MenuBar


class PressureWidget(QWidget):

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

        self._l_v_graph = DualPointPlotWidget(title="Left Velocity", y_label="m/s", d1_label="LL", d2_label="LQ")
        self._r_v_graph = DualPointPlotWidget(title="Right Velocity", y_label="m/s", d1_label="RQ", d2_label="RR")

        top_h_box.addWidget(self._l_v_graph)
        top_h_box.addWidget(self._r_v_graph)

        center_v_box.addLayout(top_h_box)
        self.setLayout(center_v_box)

        _m_client.McuDataSignal.connect(self.UpdatePlots)
        MenuBar.StartExpAction.triggered.connect(self.ClearPlots)

    @pyqtSlot()
    def ClearPlots(self):
        self._l_v_graph.ClearPlot()
        self._r_v_graph.ClearPlot()

    @pyqtSlot(MCUData)
    def UpdatePlots(self, data: MCUData):
        match data.Location:
            case Location.LL:
                self._l_v_graph.UpdateD1(data.Velocity)

            case Location.LQ:
                self._l_v_graph.UpdateD2(data.Velocity)

            case Location.RQ:
                self._r_v_graph.UpdateD1(data.Velocity)

            case Location.RR:
                self._r_v_graph.UpdateD2(data.Velocity)
