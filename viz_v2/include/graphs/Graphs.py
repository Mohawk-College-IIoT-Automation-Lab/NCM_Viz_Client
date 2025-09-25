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
            y_label: str = "label",
            x_label: str = "duration",
            color_1:str = "r",
            color_2:str = "b",
            width:int = 200,
            height:int  = 100,
            parent=None,
        ):
            super().__init__(parent)

            self.plotItem.setLabel("left", y_label)
            self.plotItem.setLabel("bottom", x_label)
            self.plotItem.setTitle(title)
            self.plotItem.showGrid(True, True, 0.5)

            self._d1_plot = self.plotItem.plot(oen=pg.mkPen(color=color_1, width=2))
            self._d2_plot = self.plotItem.plot(pen=pg.mkPen(color=color_2, width=2))

            self._buf_size = buffer_size
            self._time_counter = 0 
            self._time_np_arr = np.zeros(self._buf_size)

            self._d1_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._d2_np_arr = np.zeros(self._buf_size, dtype=np.float32)

            print(width)
            print(height)

            self.setFixedSize(width, height)

        @pyqtSlot()
        def ClearPlot(self):
            self._d1_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._d2_np_arr = np.zeros(self._buf_size, dtype=np.float32)
            self._time_np_arr = np.zeros(self._buf_size)
            self._time_counter = 0

        @pyqtSlot()
        def UpdatePlot(self, d1: float | None = None, d2: float | None = None):
            if d1 or d2 :
                self._time_np_arr = np.roll(self._time_np_arr, -1)
                self._time_np_arr[-1] = self._time_counter
                self._time_counter += 1

            if d1:
                self._d1_np_arr = np.roll(self._d1_np_arr, -1)
                self._d1_np_arr[-1] = d1
                self._d1_plot.setData(self._time_np_arr, self._d1_np_arr)

            if d2:
                self._d2_np_arr = np.roll(self._d2_np_arr, -1)
                self._d2_np_arr[-1] = d2
                self._d2_plot.setData(self._time_np_arr, self._d2_np_arr)
    
    def __init__(
            self,
            buffer_size: int = 100,
            title: str = "Title",
            y_label: str = "label",
            x_label: str = "duration",
            color_1:str = "r",
            color_2:str = "b",
            d1_label:str = "d1",
            d2_label:str = "d2",
            width:int = 400,
            height:int  = 250,
            parent=None,
        ):
        super().__init__(parent)

        self._plot = DualPointPlotWidget.DualPointPlot(buffer_size, title, y_label, x_label, color_1, color_2, width, height, parent)

        v_box = QVBoxLayout()
        legend_label = QLabel(f"{d1_label}:{color_1} - {d2_label}:{color_2}")
        legend_label.setStyleSheet("font-size: 20px;")

        v_box.addWidget(self._plot)
        v_box.addWidget(legend_label)

        self.setLayout(v_box)
        

    @pyqtSlot()
    def ClearPlot(self):
        self._plot.ClearPlot()

    @pyqtSlot()
    def UpdatePlot(self, d1: float | None = None, d2: float | None = None):
        self._plot.UpdatePlot(d1, d2)



            
