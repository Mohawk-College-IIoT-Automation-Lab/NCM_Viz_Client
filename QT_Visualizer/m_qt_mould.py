from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from QT_Visualizer.Transform import Size
from QT_Visualizer.m_qt_graphs import *
from QT_Visualizer.m_qt_sensors import * 


class MouldControlTabWidget(QWidget):
    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)