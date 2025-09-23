from logging import Handler, Formatter, StreamHandler, FileHandler, getLogger, LogRecord
from re import DEBUG
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QStatusBar
import time 

class StatusBarHandler(Handler):
    def __init__(self, status_bar:QStatusBar, msg_duration:int=1000) -> None:
        super().__init__()
        self.stat_bar = status_bar
        self.msg_dur = msg_duration

    def emit(self, record: LogRecord):
        msg = self.format(record)
        self.stat_bar.showMessage(msg, self.msg_dur)

class CustomFormatter(Formatter):
    def format(self, record) -> str:
        level = f"{record.levelname}"
        formatted_msg = f"{level} {record.msg}"
        record.msg = formatted_msg
        return super().format(record)


def initialize_logging(log_name:str, log_level = DEBUG, status_bar = None):
    log_file = f"{log_name}.log"
    logger = getLogger()
    if not logger.handlers:
        fmtter = CustomFormatter("%(asctime)s %(message)s")

        stream_handler = StreamHandler()
        stream_handler.setFormatter(fmtter)

        logger.addHandler(stream_handler)

        file_handler = FileHandler(log_file)
        file_handler.setFormatter(fmtter)

        logger.addHandler(file_handler)

        if status_bar is not None:
            status_handler = StatusBarHandler(status_bar)
            status_handler.setFormatter(fmtter)

            logger.addHandler(status_handler)

        time.sleep(1) # one second to setup

    logger.setLevel(log_level)
