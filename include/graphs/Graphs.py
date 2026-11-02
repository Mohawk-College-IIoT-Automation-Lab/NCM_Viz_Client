from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np


class DualPointPlotWidget(QWidget):
    class DualPointPlot(pg.PlotWidget):

        def __init__(
            self,
            buffer_size: int = 100,
            title: str = "Title",
            title_size: int = 24,
            y_label: str = "label",
            y_label_size: int = 20,
            x_label: str = "duration",
            x_label_size: int = 20,
            color_1: str = "#ff0000",
            color_2: str = "#ffff00",
            width: int = 200,
            height: int = 100,
            time_axis: bool = False,
            parent=None,
        ):
            # time_axis: x values are Unix time in seconds, shown as clock time
            # (local time zone) by pyqtgraph's DateAxisItem.
            axis_items = {"bottom": pg.DateAxisItem(orientation="bottom")} if time_axis else None
            super().__init__(parent, axisItems=axis_items)

            self.plotItem.setLabel(
                "left",
                f'<span style="font-size: {str(y_label_size)}px">{y_label}</span>',
            )
            self.plotItem.setLabel(
                "bottom",
                f'<span style="font-size: {str(x_label_size)}px">{x_label}</span>',
            )
            self.plotItem.setTitle(
                f'<span style="font-size: {str(title_size)}px">{title}</span>'
            )
            self.plotItem.showGrid(True, True, 0.5)
            self.plotItem.enableAutoRange(True, True)

            self._d1_plot = self.plotItem.plot(pen=pg.mkPen(color=color_1, width=2))
            self._d2_plot = self.plotItem.plot(pen=pg.mkPen(color=color_2, width=2))

            
            self._d1_plot.setClipToView(True)
            self._d2_plot.setClipToView(True)

            self._buf_size = buffer_size

            self._d1_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._d2_np_arr = np.zeros(self._buf_size, dtype=np.float32)

            # x values for the time-axis mode. float64: Unix seconds (~1.8e9)
            # in float32 would only resolve ~2 minutes.
            self._d1_t_arr = np.zeros(self._buf_size, dtype=np.float64)
            self._d2_t_arr = np.zeros(self._buf_size, dtype=np.float64)
            self._d1_count = 0  # points received since the last clear (time mode)
            self._d2_count = 0

            self.setMinimumSize(width, height)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        @pyqtSlot()
        def ClearPlot(self):
            self._d1_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._d2_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._d1_t_arr = np.zeros(self._buf_size, dtype=np.float64)
            self._d2_t_arr = np.zeros(self._buf_size, dtype=np.float64)
            self._d1_count = 0
            self._d2_count = 0

        @pyqtSlot(float)
        def UpdateD1(self, d1: float):
            self._d1_np_arr = np.roll(self._d1_np_arr, -1)
            self._d1_np_arr[-1] = d1

            self._d1_plot.setData(y=self._d1_np_arr)


        @pyqtSlot(float)
        def UpdateD2(self, d2: float):
            self._d2_np_arr = np.roll(self._d2_np_arr, -1)
            self._d2_np_arr[-1] = d2

            self._d2_plot.setData(y = self._d2_np_arr)

        # --- time-axis mode: each point has its own x (Unix seconds) -------
        # Only the points received so far are drawn, so the empty buffer
        # (x = 0, i.e. 1970) never stretches the axis.

        @pyqtSlot(float, float)
        def UpdateD1At(self, t: float, d1: float):
            self._d1_t_arr = np.roll(self._d1_t_arr, -1)
            self._d1_np_arr = np.roll(self._d1_np_arr, -1)
            self._d1_t_arr[-1] = t
            self._d1_np_arr[-1] = d1
            self._d1_count = min(self._d1_count + 1, self._buf_size)

            n = self._d1_count
            self._d1_plot.setData(x=self._d1_t_arr[-n:], y=self._d1_np_arr[-n:])

        @pyqtSlot(float, float)
        def UpdateD2At(self, t: float, d2: float):
            self._d2_t_arr = np.roll(self._d2_t_arr, -1)
            self._d2_np_arr = np.roll(self._d2_np_arr, -1)
            self._d2_t_arr[-1] = t
            self._d2_np_arr[-1] = d2
            self._d2_count = min(self._d2_count + 1, self._buf_size)

            n = self._d2_count
            self._d2_plot.setData(x=self._d2_t_arr[-n:], y=self._d2_np_arr[-n:])

    def __init__(
        self,
        buffer_size: int = 100,
        title: str = "Title",
        title_size: int = 24,
        y_label: str = "label",
        y_label_size: int = 20,
        x_label: str = "duration",
        x_label_size: int = 20,
        d1_label: str = "d1",
        color_1: str = "#ff0000",
        d2_label: str = "d2",
        color_2: str = "#ffff00",
        width: int = 200,
        height: int = 100,
        time_axis: bool = False,
        parent=None,
    ):
        super().__init__(parent)

        self._plot = DualPointPlotWidget.DualPointPlot(
            buffer_size,
            title,
            title_size,
            y_label,
            y_label_size,
            x_label,
            x_label_size,
            color_1,
            color_2,
            width,
            height,
            time_axis,
            parent,
        )

        v_box = QVBoxLayout()
        label_h_box = QHBoxLayout()
        _d1_label = QLabel(f"{d1_label}")
        _d1_label.setStyleSheet(f"font-size: 20px; color: {color_1}")
        _d2_label = QLabel(f"{d2_label}")
        _d2_label.setStyleSheet(f"font-size: 20px; color: {color_2}")

        label_h_box.addWidget(_d1_label)
        label_h_box.addWidget(_d2_label)

        v_box.addWidget(self._plot)
        v_box.addLayout(label_h_box)

        self.setLayout(v_box)

    @pyqtSlot()
    def ClearPlot(self):
        self._plot.ClearPlot()

    @pyqtSlot(float)
    def UpdateD1(self, d1: float):
        self._plot.UpdateD1(d1)

    @pyqtSlot(float)
    def UpdateD2(self, d2: float):
        self._plot.UpdateD2(d2)

    @pyqtSlot(float, float)
    def UpdateD1At(self, t: float, d1: float):
        self._plot.UpdateD1At(t, d1)

    @pyqtSlot(float, float)
    def UpdateD2At(self, t: float, d2: float):
        self._plot.UpdateD2At(t, d2)
