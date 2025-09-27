from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar
import time

from paho.mqtt.client import MQTTv31


from .Mqtt import MqttClient
from .MenuBar import MenuBar
from .SenWidget import SenWidget
from .PlotsWidget import PlotsWidget
from .DataViewWidget import DataViewWidget
import logging


class StatusBarHandler(logging.Handler):
    def __init__(self, status_bar: QStatusBar, msg_duration: int = 5000) -> None:
        super().__init__()
        self.stat_bar = status_bar
        self.msg_dur = msg_duration

    def emit(self, record) -> None:
        try:
            msg = self.format(record)
            print(msg)
            self.stat_bar.showMessage(msg, self.msg_dur)
        except Exception:
            self.handleError(record)


def initialize_logging(
    log_name: str, log_level=logging.DEBUG, status_bar: QStatusBar | None = None
):
    log_file = f"{log_name}.log"
    logger = logging.getLogger()
    fmtter = logging.Formatter("[%(asctime)s]-[%(levelname)s]: %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(fmtter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmtter)
    logger.addHandler(file_handler)

    if status_bar is not None:
        status_handler = StatusBarHandler(status_bar)
        status_handler.setLevel(logging.INFO)
        status_handler.setFormatter(fmtter)
        logger.addHandler(status_handler)

    time.sleep(1)  # one second to setup

    logger.setLevel(log_level)


def set_dark_mode(win: QMainWindow):

    dark = QtGui.QPalette()
    dark.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.Base, QtGui.QColor(55, 55, 55))
    dark.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
    dark.setColor(
        QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor(127, 127, 127)
    )
    dark.setColor(
        QtGui.QPalette.Disabled,
        QtGui.QPalette.ButtonText,
        QtGui.QColor(127, 127, 127),
    )

    win.setPalette(dark)


class MainWindow(QMainWindow):

    LOG_FMT_STR = f"[Main] - %s"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initialize_logging(log_name="Qt", status_bar=self.statusBar())
        m_client = MqttClient.get_instance()

        set_dark_mode(self)

        self.setWindowTitle("Nexus Control Module Vizulation Software")
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        logging.debug(MainWindow.LOG_FMT_STR, "Creating MainWindow")

        menu_bar = MenuBar(self)
        self.setMenuBar(menu_bar)

        tab_widget = QTabWidget()

        sen_tab_widget = SenWidget()
        graph_tab_widget = PlotsWidget()
        data_tab_widget = DataViewWidget()

        tab_widget.setGeometry(0, 0, 500, 500)
        tab_widget.addTab(sen_tab_widget, "SEN")
        tab_widget.addTab(graph_tab_widget, "Graphs")
        tab_widget.addTab(data_tab_widget, "Dataview")

        central_v_box = QVBoxLayout(central_widget)
        central_v_box.addWidget(tab_widget)
        central_widget.setLayout(central_v_box)

        self.showMaximized()
        logging.debug(MainWindow.LOG_FMT_STR, "Maximizaing MainWindow")

    def closeEvent(self, a0) -> None:
        m_client = MqttClient.get_instance()
        m_client.DisconnectBroker()
        return super().closeEvent(a0)
