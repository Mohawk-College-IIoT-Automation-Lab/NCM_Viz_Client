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
            color_2: str = "#0000ff",
            width: int = 200,
            height: int = 100,
            parent=None,
        ):
            super().__init__(parent)

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

            self._d1_plot = self.plotItem.plot(oen=pg.mkPen(color=color_1, width=2))
            self._d2_plot = self.plotItem.plot(pen=pg.mkPen(color=color_2, width=2))

            self._buf_size = buffer_size

            self._d1_counter = 0
            self._d2_counter = 0
            self._d1_t_np_arr = np.zeros(self._buf_size)
            self._d2_t_np_arr = np.zeros(self._buf_size)

            self._d1_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._d2_np_arr = np.zeros(self._buf_size, dtype=np.float32)

            self.setMinimumSize(width, height)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        @pyqtSlot()
        def ClearPlot(self):
            self._d1_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._d2_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._d1_t_np_arr = np.zeros(self._buf_size)
            self._d2_t_np_arr = np.zeros(self._buf_size)
            self._d1_counter = 0
            self._d2_counter = 0

        @pyqtSlot(float)
        def UpdateD1(self, d1: float):
            self._d1_np_arr = np.roll(self._d1_np_arr, -1)
            self._d1_np_arr[-1] = d1

            self._d1_t_np_arr = np.roll(self._d1_t_np_arr, -1)
            self._d1_t_np_arr[-1] = self._d1_counter 
            self._d1_counter += 1

            self._d1_plot.setData(self._d1_t_np_arr, self._d1_np_arr)


        @pyqtSlot(float)
        def UpdateD2(self, d2: float):
            self._d2_np_arr = np.roll(self._d2_np_arr, -1)
            self._d2_np_arr[-1] = d2

            self._d2_t_np_arr = np.roll(self._d2_t_np_arr, -1)
            self._d2_t_np_arr[-1] = self._d2_counter 
            self._d2_counter += 1

            self._d2_plot.setData(self._d2_t_np_arr, self._d2_np_arr)

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
            parent,
        )

        v_box = QVBoxLayout()
        label_h_box = QHBoxLayout()
        _d1_label = QLabel(f"{d1_label}:{color_1}")
        _d1_label.setStyleSheet(f"font-size: 20px; color: {color_1}")
        _d2_label = QLabel(f"{d2_label}:{color_2}")
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
