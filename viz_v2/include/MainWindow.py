from re import DEBUG
from PyQt5.QtWidgets import QMainWindow, QWidget

from .Logger import initialize_logging
import logging

LOG_LEADER = "QT"

def getLogStr(msg:str):
    return f"[{LOG_LEADER}] - {msg}"

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        window_title = "Nexus Control Module Vizulation Software"
        self.setWindowTitle(window_title)
        central_widget = QWidget(self)

        initialize_logging(log_name="Qt", log_level=DEBUG, status_bar=self.statusBar())
        logging.debug(getLogStr("Creating MainWindow"))

        # Load settings 

        # Setup Menu bar 

        # Set Central widget -> tab widget

        self.showMaximized()




