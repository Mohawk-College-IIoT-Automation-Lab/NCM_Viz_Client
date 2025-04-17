from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QPalette
from dimensions import Dimension
import sys, os, PyQt5
import pyqtgraph as pg
import numpy as np

class DistanceGraph(pg.PlotWidget):

    def __init__(self, buffer_size:int=600, approx_display_rate:int=30, isLeft:bool=False, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        
        disp_int = 1 / 30

        self.plotItem.setLabel("left", "Distance", units="mm")
        self.plotItem.setLabel("bottom", "Duration", units=f"{disp_int:.3}s")

        if isLeft:
            self.plotItem.setTitle(f"Left of Mould (LL, LQ) {approx_display_rate}Hz")
        else:
            self.plotItem.setTitle(f"Right of Mould (RQ, RR) {approx_display_rate}Hz")
        self.plotItem.showGrid(True, True, 0.5) # 0.5 oppacity

        self.inside_sensor_plot = self.plotItem.plot(pen=pg.mkPen(color='y', width=2))
        self.outside_sensor_plot = self.plotItem.plot(pen=pg.mkPen(color='y', width=2))

        self.buffer_size = buffer_size

        self.time_data_ticker = 0
        self.time_data = np.zeros(self.buffer_size)
        self.inside_data = np.zeros(self.buffer_size, dtype=np.float32)
        self.outside_data = np.zeros(self.buffer_size, dtype=np.float32)

    @pyqtSlot()
    def update_plot(self, inside_sensor:float, outside_sensor:float):

        self.inside_data = np.roll(self.inside_data, -1)
        self.inside_data[-1] = inside_sensor

        self.outside_data = np.roll(self.outside_data, -1)
        self.outside_data[-1] = outside_sensor

        self.time_data = np.roll(self.time_data, -1)
        self.time_data[-1] = self.time_data_ticker

        self.time_data_ticker += 1

        self.inside_sensor_plot.setData(self.time_data, self.inside_data)
        self.outside_sensor_plot.setData(self.time_data, self.outside_data)


class AlarmLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAutoFillBackground(True)
        self.state = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_style()

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