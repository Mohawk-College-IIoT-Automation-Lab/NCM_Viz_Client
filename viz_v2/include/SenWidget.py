from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PyQt5.QtCore import pyqtSlot, Qt

from .qml.gauge import GaugeWidget
from .qml.sen import SenAnimWidget
from .graphs.Graphs import DualPointPlotWidget
from .DataStructures import SensorData, SenTelemetry
from .Mqtt import MqttClient
from .DataViewWidget import DataViewWidget


class SenWidget(QWidget):

    LOG_FMT_STR = f"[SEN] - %s"

    def __init__(self, parent=None):
        super().__init__(parent)

        _m_client = MqttClient.get_instance()

        """ A central H box will hold 3 v boxs 
            - The left most vbox will be gauges
            - The center will be the sen animation
            - The right most vbox will be telemetry graphs
        """

        center_h_box = QHBoxLayout(self)

        # Left V Box

        self._ll_wl = GaugeWidget(title="LL Waterlevel")
        self._lq_wl = GaugeWidget(title="LQ Waterlevel")
        self._rq_wl = GaugeWidget(title="RQ Waterlevel")
        self._rr_wl = GaugeWidget(title="RR Waterlevel")

        self._ll_v = GaugeWidget(title="LL Velocity")
        self._lq_v = GaugeWidget(title="LQ Velocity")
        self._rq_v = GaugeWidget(title="RQ Velocity")
        self._rr_v = GaugeWidget(title="RR Velocity")

        gauge_g_box = QGridLayout()

        gauge_g_box.addWidget(self._ll_wl, 0, 0)
        gauge_g_box.addWidget(self._lq_wl, 0, 1)
        gauge_g_box.addWidget(self._rq_wl, 0, 2)
        gauge_g_box.addWidget(self._rr_wl, 0, 3)

        gauge_g_box.addWidget(self._ll_v, 1, 0)
        gauge_g_box.addWidget(self._lq_v, 1, 1)
        gauge_g_box.addWidget(self._rq_v, 1, 2)
        gauge_g_box.addWidget(self._rr_v, 1, 3)

        center_h_box.addLayout(gauge_g_box)

        # Center V Box
        anim_v_box = QVBoxLayout()
        btn_g_box = QGridLayout()

        l_m10_pbtn = QPushButton("-10%")
        l_m10_pbtn.clicked.connect(lambda: _m_client.SenLJogPercent(-10))
        l_m5_pbtn = QPushButton("-5%")
        l_m5_pbtn.clicked.connect(lambda: _m_client.SenLJogPercent(-5))
        l_p5_pbtn = QPushButton("+5%")
        l_p5_pbtn.clicked.connect(lambda: _m_client.SenLJogPercent(5))
        l_p10_pbtn = QPushButton("+10%")
        l_p10_pbtn.clicked.connect(lambda: _m_client.SenLJogPercent(10))
        l_h_pbtn = QPushButton("Home left")
        l_h_pbtn.clicked.connect(lambda: _m_client.SenLHome())
        l_c_pbtn = QPushButton("Close left")
        l_c_pbtn.clicked.connect(lambda: _m_client.SenLClose())

        r_m10_pbtn = QPushButton("-10%")
        r_m10_pbtn.clicked.connect(lambda: _m_client.SenRJogPercent(-10))
        r_m5_pbtn = QPushButton("-5%")
        r_m5_pbtn.clicked.connect(lambda: _m_client.SenRJogPercent(-5))
        r_p5_pbtn = QPushButton("+5%")
        r_p5_pbtn.clicked.connect(lambda: _m_client.SenRJogPercent(5))
        r_p10_pbtn = QPushButton("+10%")
        r_p10_pbtn.clicked.connect(lambda: _m_client.SenRJogPercent(10))
        r_h_pbtn = QPushButton("Home right")
        r_h_pbtn.clicked.connect(lambda: _m_client.SenRHome())
        r_c_pbtn = QPushButton("Close right")
        r_c_pbtn.clicked.connect(lambda: _m_client.SenRClose())

        btn_g_box.addWidget(l_p10_pbtn, 0, 0)
        btn_g_box.addWidget(l_m10_pbtn, 0, 1)
        btn_g_box.addWidget(r_p10_pbtn, 0, 2)
        btn_g_box.addWidget(r_m10_pbtn, 0, 3)
        btn_g_box.addWidget(l_p5_pbtn, 1, 0)
        btn_g_box.addWidget(l_m5_pbtn, 1, 1)
        btn_g_box.addWidget(r_p5_pbtn, 1, 2)
        btn_g_box.addWidget(r_m5_pbtn, 1, 3)
        btn_g_box.addWidget(l_h_pbtn, 2, 0)
        btn_g_box.addWidget(l_c_pbtn, 2, 1)
        btn_g_box.addWidget(r_h_pbtn, 2, 2)
        btn_g_box.addWidget(r_c_pbtn, 2, 3)

        self._sen = SenAnimWidget()
        anim_v_box.addWidget(self._sen)
        anim_v_box.addLayout(btn_g_box)
        anim_v_box.addStretch()
        center_h_box.addLayout(anim_v_box)

        # Right V Box
        tele_v_box = QVBoxLayout()
        _d1_label = "Left"
        _d2_label = "Right"

        self._t_pos = DualPointPlotWidget(
            title="Position", y_label="Ticks", d1_label=_d1_label, d2_label=_d2_label
        )
        self._t_vel = DualPointPlotWidget(
            title="Velocity", y_label="Ticks/s", d1_label=_d1_label, d2_label=_d2_label
        )
        self._t_curr = DualPointPlotWidget(
            title="Current", y_label="mA", d1_label=_d1_label, d2_label=_d2_label
        )

        tele_v_box.addWidget(self._t_pos)
        tele_v_box.addWidget(self._t_vel)
        tele_v_box.addWidget(self._t_curr)
        center_h_box.addLayout(tele_v_box)

        self.setLayout(center_h_box)

        _m_client.DaqDataSignal.connect(self._DaqDataSlot)
        _m_client.SenTeleLeftSignal.connect(self._SenLeftTeleSlot)
        _m_client.SenTeleRightSignal.connect(self._SenRightTeleSlot)

    @pyqtSlot(SensorData)
    def _DaqDataSlot(self, data: SensorData):
        if data:
            self._ll_wl.setProperty("value", data.Ultra_Sonic_Distance.LL)
            self._lq_wl.setProperty("value", data.Ultra_Sonic_Distance.LQ)
            self._rq_wl.setProperty("value", data.Ultra_Sonic_Distance.RQ)
            self._rr_wl.setProperty("value", data.Ultra_Sonic_Distance.RR)

            self._ll_v.setProperty("value", data.Anemometer.LL)
            self._lq_v.setProperty("value", data.Anemometer.LQ)
            self._rq_v.setProperty("value", data.Anemometer.RQ)
            self._rr_v.setProperty("value", data.Anemometer.RR)

    @pyqtSlot(SenTelemetry)
    def _SenLeftTeleSlot(self, tele: SenTelemetry):
        if tele:
            self._sen.SetLeftPort(tele.present_telemetry.percent)
            self._t_pos.UpdateD1(float(tele.present_telemetry.position))
            self._t_vel.UpdateD1(float(tele.present_telemetry.velocity))
            self._t_curr.UpdateD1(float(tele.present_telemetry.current))

    @pyqtSlot(SenTelemetry)
    def _SenRightTeleSlot(self, tele: SenTelemetry):
        if tele:
            self._sen.SetRightPort(tele.present_telemetry.percent)
            self._t_pos.UpdateD2(tele.present_telemetry.position)
            self._t_vel.UpdateD2(tele.present_telemetry.velocity)
            self._t_curr.UpdateD2(tele.present_telemetry.current)
