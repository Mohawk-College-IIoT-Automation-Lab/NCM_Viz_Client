from PyQt5.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSlot, Qt

import logging

from .qml.gauge import GaugeWidget
from .qml.sen import SenAnimWidget
from .graphs.Graphs import DualPointPlotWidget
from .DataStructures import SensorData, SenTelemetry
from .Mqtt import MqttClient


class SenWidget(QWidget):

    LOG_FMT_STR = f"[SEN] - %s"

    def __init__(self, parent = None):
        super().__init__(parent)

        _m_client = MqttClient.get_instance()

        """ A central H box will hold 3 v boxs 
            - The left most vbox will be gauges
            - The center will be the sen animation
            - The right most vbox will be telemetry graphs
        """

        center_h_box = QHBoxLayout(self)

        # Left V Box
        gauge_v_box = QVBoxLayout()

        self._ll_wl = GaugeWidget(title="LL Waterlevel")
        self._lq_wl = GaugeWidget(title="LQ Waterlevel")
        self._rq_wl = GaugeWidget(title="RQ Waterlevel")
        self._rr_wl = GaugeWidget(title="RR Waterlevel")

        self._ll_v = GaugeWidget(title="LL Velocity")
        self._lq_v = GaugeWidget(title="LQ Velocity")
        self._rq_v = GaugeWidget(title="RQ Velocity")
        self._rr_v = GaugeWidget(title="RR Velocity")

        gauge_top_h_box = QHBoxLayout()
        gauge_bot_h_box = QHBoxLayout()

        gauge_top_h_box.addWidget(self._ll_wl)
        gauge_top_h_box.addWidget(self._lq_wl)
        gauge_top_h_box.addWidget(self._rq_wl)
        gauge_top_h_box.addWidget(self._rr_wl)

        gauge_bot_h_box.addWidget(self._ll_v)
        gauge_bot_h_box.addWidget(self._lq_v)
        gauge_bot_h_box.addWidget(self._rq_v)
        gauge_bot_h_box.addWidget(self._rr_v)

        gauge_v_box.addLayout(gauge_top_h_box)
        gauge_v_box.addLayout(gauge_bot_h_box)
        center_h_box.addLayout(gauge_v_box)

        # Center V Box
        anim_v_box = QVBoxLayout()

        self._sen = SenAnimWidget()
        anim_v_box.addWidget(self._sen)

        center_h_box.addLayout(anim_v_box)

        # Right V Box
        tele_v_box = QVBoxLayout()

        self._t_pos = DualPointPlotWidget(title="Position", y_label="Ticks", d1_label="Left", d2_label="Right")
        self._t_vel = DualPointPlotWidget(title="Velocity", y_label="Ticks/s", d1_label="Left", d2_label="Right")

        tele_v_box.addWidget(self._t_pos)
        tele_v_box.addWidget(self._t_vel)
        center_h_box.addLayout(tele_v_box)

        self.setLayout(center_h_box)

        _m_client.DaqDataSignal.connect(self._DaqDataSlot)
        _m_client.SenTeleLeftSignal.connect(self._SenLeftTeleSlot)
        _m_client.SenTeleRightSignal.connect(self._SenRightTeleSlot)

    @pyqtSlot()
    def _DaqDataSlot(self, data: SensorData | None = None):
        if data:
            # do something
            pass

    @pyqtSlot()
    def _SenLeftTeleSlot(self, tele: SenTelemetry | None = None):
        if tele:
            # do something
            pass

    @pyqtSlot()
    def _SenRightTeleSlot(self, tele: SenTelemetry | None = None):
        if tele:
            # do something
            pass
