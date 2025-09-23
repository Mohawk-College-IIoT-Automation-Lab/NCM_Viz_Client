from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar
import time

from .MenuBar import MenuBar
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


def initialize_logging(log_name: str, log_level=logging.DEBUG, status_bar=None):
    log_file = f"{log_name}.log"
    logger = logging.getLogger()
    fmtter = logging.Formatter('[%(asctime)s]-[%(levelname)s]: %(message)s')

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

class MainWindow(QMainWindow):

    LOG_FMT_STR = f"[Main] - %s"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        window_title = "Nexus Control Module Vizulation Software"
        self.setWindowTitle(window_title)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        initialize_logging(log_name="Qt", status_bar=self.statusBar())

        logging.debug(MainWindow.LOG_FMT_STR, "Creating MainWindow")

        menu_bar = MenuBar(self)
        self.setMenuBar(menu_bar)

        # replace all w/ custom
        tab_widget = QTabWidget()
        sen_tab_widget = QWidget()
        graph_tab_widget = QWidget()
        data_tab_widget = QWidget()

        tab_widget.setGeometry(0, 0, 500, 500)
        tab_widget.addTab(sen_tab_widget, "SEN")
        tab_widget.addTab(graph_tab_widget, "Graphs")
        tab_widget.addTab(data_tab_widget, "Dataview")

        central_v_box = QVBoxLayout(central_widget)
        central_v_box.addWidget(tab_widget)
        central_widget.setLayout(central_v_box)

        self.showMaximized()
        logging.debug(MainWindow.LOG_FMT_STR, "Maximizaing MainWindow")

