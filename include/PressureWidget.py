from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSlot

import logging
import time

from .graphs.Graphs import DualPointPlotWidget
from .graphs.Bars import SignedBarWidget, GroupedBarWidget
from .DataStructures import MCUData, Location
from .Mqtt import MqttClient
from .MenuBar import MenuBar


class PressureWidget(QWidget):
    """MCU sensor system: velocity over time, plus instantaneous bars.

    A central V box holds three rows:
      - top: two DualPointPlotWidget time series of velocity, LL/LQ on the
        left plot and RQ/RR on the right
      - middle: an H box of four signed horizontal velocity bars, one per
        location, ordered LL, LQ, RQ, RR left to right (-5 to +5 m/s)
      - bottom: a grouped bar chart of pressures, two bar sets (CH1, CH2)
        across the four locations (950 to 1200 mbar)

    Every location has its own MCU and they all publish to the same topic,
    so each message updates one time-series trace, one velocity bar and one
    pressure column. Pressure columns are cached here; a location that stops
    publishing holds its last reading rather than dropping to zero.
    """

    LOG_FMT_STR = "[PressureWidget] - %s"

    # Declaration order in the Location StrEnum drives left-to-right order.
    LOCATIONS = tuple(Location)

    VEL_MIN = -5.0
    VEL_MAX = 5.0

    PRESSURE_MIN = 950.0
    PRESSURE_MAX = 1200.0

    CH1 = "CH1"
    CH2 = "CH2"

    CH1_COLOR = "#ff0000"
    NEGATIVE_COLOR = "#ff0000"
    POSITIVE_COLOR = "#50C878"
    CH2_COLOR = "#e6c200"

    def __init__(self, parent=None):
        super().__init__(parent)

        _m_client = MqttClient.get_instance()

        logging.debug(PressureWidget.LOG_FMT_STR, "Creating PressureWidget")

        self._loc_index = {loc: i for i, loc in enumerate(PressureWidget.LOCATIONS)}

        # One cached column per bar set; a message only ever fills one index.
        self._pressures = {
            PressureWidget.CH1: [PressureWidget.PRESSURE_MIN] * len(PressureWidget.LOCATIONS),
            PressureWidget.CH2: [PressureWidget.PRESSURE_MIN] * len(PressureWidget.LOCATIONS),
        }

        center_v_box = QVBoxLayout(self)

        # --- row 1: velocity over time -----------------------------------
        top_h_box = QHBoxLayout()

        self._l_v_graph = DualPointPlotWidget(
            title="Left Velocity", y_label="m/s", x_label="time",
            d1_label="LL", d2_label="LQ", time_axis=True,
        )
        self._r_v_graph = DualPointPlotWidget(
            title="Right Velocity", y_label="m/s", x_label="time",
            d1_label="RQ", d2_label="RR", time_axis=True,
        )

        top_h_box.addWidget(self._l_v_graph)
        top_h_box.addWidget(self._r_v_graph)

        # --- row 2: instantaneous signed velocity bars --------------------
        bars_h_box = QHBoxLayout()

        self._vel_bars = {}
        for loc in PressureWidget.LOCATIONS:
            bar = SignedBarWidget(
                title=loc.value,
                units="m/s",
                v_min=PressureWidget.VEL_MIN,
                v_max=PressureWidget.VEL_MAX,
                pos_color=PressureWidget.POSITIVE_COLOR,
                neg_color=PressureWidget.NEGATIVE_COLOR,
            )
            self._vel_bars[loc] = bar
            bars_h_box.addWidget(bar)

        # --- row 3: instantaneous pressures -------------------------------
        self._pressure_barset = GroupedBarWidget(
            categories=[loc.value for loc in PressureWidget.LOCATIONS],
            set_labels=(PressureWidget.CH1, PressureWidget.CH2),
            title="Pressure",
            y_label="mbar",
            y_min=PressureWidget.PRESSURE_MIN,
            y_max=PressureWidget.PRESSURE_MAX,
            colors=(PressureWidget.CH1_COLOR, PressureWidget.CH2_COLOR),
            height=220,
        )

        center_v_box.addLayout(top_h_box, 3)
        center_v_box.addLayout(bars_h_box, 2)
        center_v_box.addWidget(self._pressure_barset, 3)
        self.setLayout(center_v_box)

        _m_client.McuDataSignal.connect(self.UpdatePlots)
        MenuBar.PrepareExpAction.triggered.connect(self.ClearPlots)

    @pyqtSlot()
    def ClearPlots(self):
        self._l_v_graph.ClearPlot()
        self._r_v_graph.ClearPlot()

        for bar in self._vel_bars.values():
            bar.ClearBar()

        for column in self._pressures.values():
            for i in range(len(column)):
                column[i] = PressureWidget.PRESSURE_MIN

        self._pressure_barset.ClearBars()

    @pyqtSlot(MCUData)
    def UpdatePlots(self, data: MCUData):
        # x = the batch's timestamp in Unix seconds (shown as clock time).
        # Publishers without a Timestamp fall back to the arrival time.
        t = data.Timestamp / 1e6 if data.Timestamp is not None else time.time()

        # Velocity over time - which plot and which trace depends on location.
        match data.Location:
            case Location.LL:
                self._l_v_graph.UpdateD1At(t, data.Velocity)

            case Location.LQ:
                self._l_v_graph.UpdateD2At(t, data.Velocity)

            case Location.RQ:
                self._r_v_graph.UpdateD1At(t, data.Velocity)

            case Location.RR:
                self._r_v_graph.UpdateD2At(t, data.Velocity)

            case _:
                logging.warning(
                    PressureWidget.LOG_FMT_STR,
                    f"Unknown location: {data.Location}",
                )
                return

        # Instantaneous velocity bar for this location.
        self._vel_bars[data.Location].SetValue(data.Velocity)

        # Instantaneous pressure: fill this location's column in both sets.
        index = self._loc_index[data.Location]
        self._pressures[PressureWidget.CH1][index] = data.Pressure.CH1
        self._pressures[PressureWidget.CH2][index] = data.Pressure.CH2

        self._pressure_barset.SetByLabel(
            PressureWidget.CH1, self._pressures[PressureWidget.CH1]
        )
        self._pressure_barset.SetByLabel(
            PressureWidget.CH2, self._pressures[PressureWidget.CH2]
        )
