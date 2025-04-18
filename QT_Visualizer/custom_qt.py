from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from Transform import Size
import pyqtgraph as pg
import numpy as np

class QCustomGraphsWidget(QWidget):

    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)

        self.main_v_box = QVBoxLayout(self)
        self.top_h_box = QHBoxLayout()

        self.left_graph = Q2SensorsGraph(title="Left Mould (LL, LQ)", size=Size(300, 300))
        self.right_graph = Q2SensorsGraph(title="Right Mould (RQ, RR)", size=Size(300, 300))
        self.standing_wave_graph = Q2SensorsGraph(title="Stating Wave Height (LL-LQ) (RR-RQ)", size=Size(600, 300))

        self.top_h_box.addWidget(self.left_graph)
        self.top_h_box.addWidget(self.right_graph)
        self.main_v_box.addLayout(self.top_h_box)
        self.main_v_box.addWidget(self.standing_wave_graph)


    @pyqtSlot()
    def update_plot(self, ll_value:float, lq_value:float, rq_value:float, rr_value:float):
        left_standing_wave = ll_value - lq_value
        right_standing_wave = rr_value - rq_value
        
        self.left_graph.update_plot(lq_value, ll_value)
        self.right_graph.update_plot(rq_value, rr_value)
        self.standing_wave_graph.update_plot(left_standing_wave, right_standing_wave)


class QSingleSensorGraph(pg.PlotWidget):
    def __init__(self, buffer_size:int=600, approx_display_rate:int=30, title:str="Default Title", parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        
        disp_int = 1 / approx_display_rate

        self.plotItem.setLabel("left", "Distance", units="mm")
        self.plotItem.setLabel("bottom", "Duration", units=f"{disp_int:.3}s")

        self.plotItem.setTitle(title)
        self.plotItem.showGrid(True, True, 0.5) # 0.5 oppacity

        self.buffer_size = buffer_size
        self.time_data_ticker = 0
        self.time_data = np.zeros(self.buffer_size)

        self.sensor_data = np.zeros(self.buffer_size, dtype=np.float32)

        self.sensor_plot = self.plotItem.plot(pen=pg.mkPen(color='y', width=2))

    @pyqtSlot()
    def update_plot(self, sensor_data:float):

        self.sensor_data = np.roll(self.sensor_data, -1)
        self.sensor_data[-1] = sensor_data

        self.time_data = np.roll(self.time_data, -1)
        self.time_data[-1] = self.time_data_ticker

        self.time_data_ticker += 1

        self.sensor_plot.setData(self.time_data, self.sensor_data)

class Q2SensorsGraph(pg.PlotWidget):

    DEFAULT_SIZE = Size(300, 300)

    def __init__(self, size:Size=DEFAULT_SIZE, buffer_size = 600, approx_display_rate = 30, title = "Default Title", parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        
        disp_int = 1 / approx_display_rate

        self.setFixedSize(size.w, size.h)

        self.plotItem.setLabel("left", "Distance", units="mm")
        self.plotItem.setLabel("bottom", "Duration", units=f"{disp_int:.3}s")

        self.plotItem.setTitle(title)
        self.plotItem.showGrid(True, True, 0.5) # 0.5 oppacity

        self.buffer_size = buffer_size
        self.time_data_ticker = 0
        self.time_data = np.zeros(self.buffer_size)

        self.data_1_plot = self.plotItem.plot(pen=pg.mkPen(color='y', width=2))
        self.data_2_plot = self.plotItem.plot(pen=pg.mkPen(color='y', width=2))


        self.data_1 = np.zeros(self.buffer_size, dtype=np.float32)
        self.data_2 = np.zeros(self.buffer_size, dtype=np.float32)

    @pyqtSlot()
    def update_plot(self, data_1:float, data_2:float):
        self.data_1 = np.roll(self.data_1, -1)
        self.data_1[-1] = data_1

        self.data_2 = np.roll(self.data_2, -1)
        self.data_2[-1] = data_2

        self.time_data = np.roll(self.time_data, -1)
        self.time_data[-1] = self.time_data_ticker

        self.time_data_ticker += 1

        self.data_1_plot.setData(self.time_data, self.data_1)
        self.data_2_plot.setData(self.time_data, self.data_2)



class AlarmLabel(QLabel):

    DEFAULT_SIZE = Size(100, 25)

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAutoFillBackground(True)
        self.state = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_style()
        self.setFixedHeight(AlarmLabel.DEFAULT_SIZE.h)

    @pyqtSlot()
    def on(self):
        self.state = True
        self.update_style()

    @pyqtSlot()
    def off(self):
        self.state = False
        self.update_style()

    @pyqtSlot()
    def toggle(self):
        self.state = not self.state
        self.update_style()

    def update_style(self):
        palette = self.palette()
        color = QColor("lightgreen") if self.state else QColor("lightcoral")
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)