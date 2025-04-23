from PyQt5.QtWidgets import QStatusBar, QToolBar, QMainWindow, QAction, QMenuBar
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from m_qobject import M_QObject





class M_QActions(M_QObject):

    start_exp_signal = pyqtSignal()
    stop_exp_signal = pyqtSignal()
    reset_exp_signal = pyqtSignal()

    def __init__(self, status_bar:QStatusBar, parent:QMainWindow, host_name:str="localhost", host_port:int=1883):
        super().__init__(status_bar, host_name, host_port, parent=parent)

        tool_bar = QToolBar("Experiment Control", parent)
        tool_bar.setMovable(False)
        tool_bar.setFloatable(False)


        start_exp_action = QAction("Start Experiment", self)


