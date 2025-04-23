from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from Transform import Size
from m_qt_graphs import *
from m_qt_sensors import * 


class MouldControlTabWidget(QWidget):
    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)