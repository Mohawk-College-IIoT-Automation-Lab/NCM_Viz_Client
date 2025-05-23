import PyQt5.Qt
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QSizePolicy
from .Transform import Size
import pyqtgraph as pg
import numpy as np

class QSingleSensorGraph(pg.PlotWidget):

    DEFAULT_SIZE = Size(600, 300)

    def __init__(self, buffer_size:int=300, approx_display_rate:int=30, title:str="Default Title", parent=None, background='default', plotItem=None, **kargs):
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

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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

    def __init__(self, size:Size=DEFAULT_SIZE, color_1:str='r', color_2:str='y', buffer_size = 300, approx_display_rate = 30, title = "Default Title", parent=None, background='default', label:str = "Distance", units:str = "mm", plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        
        self.disp_int = 1 / approx_display_rate

        self.plotItem.setLabel("left", label, units=units)
        self.plotItem.setLabel("bottom", "Duration", units=f"{self.disp_int:.3}s")

        self.plotItem.setTitle(title)
        self.plotItem.showGrid(True, True, 0.5) # 0.5 oppacity

        self.buffer_size = buffer_size
        self.time_data_ticker = 0
        self.time_data = np.zeros(self.buffer_size)

        self.data_1_plot = self.plotItem.plot(pen=pg.mkPen(color=color_1, width=2))
        self.data_2_plot = self.plotItem.plot(pen=pg.mkPen(color=color_2, width=2))

        self.data_1 = np.zeros(self.buffer_size, dtype=np.float32)
        self.data_2 = np.zeros(self.buffer_size, dtype=np.float32)

        self.clear_plot()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    @pyqtSlot()
    def clear_plot(self):
        self.data_1 = np.zeros(self.buffer_size, dtype=np.float32)
        self.data_2 = np.zeros(self.buffer_size, dtype=np.float32)
        self.time_data = np.zeros(self.buffer_size)
        self.time_data_ticker = 0

    @pyqtSlot(float, float)
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

