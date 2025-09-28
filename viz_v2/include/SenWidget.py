from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import pyqtSlot

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
        self._sen_data = DataViewWidget.SenTeleTree()
        anim_v_box.addWidget(self._sen)

        _sen_label = QLabel("Sen Data")
        _sen_label.setStyleSheet("font-size: 24px; color: #ffffff;")
        anim_v_box.addWidget(_sen_label)
        
        anim_v_box.addWidget(self._sen_data)
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
            self._sen.SetPortValue(leftPort=tele.present_telemetry.percent)
            self._sen_data.UpdateLeft(tele)

    @pyqtSlot(SenTelemetry)
    def _SenRightTeleSlot(self, tele: SenTelemetry):
        if tele:
            self._sen.SetPortValue(rightPort=tele.present_telemetry.percent)
            self._sen_data.UpdateRight(tele)
