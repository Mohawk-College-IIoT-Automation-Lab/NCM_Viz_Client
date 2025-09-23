from logging import Handler, Formatter, StreamHandler, FileHandler, getLogger, LogRecord
from re import DEBUG
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import time 

class QLogging(Handler, QObject):

    Message = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

    def emit(self, record: LogRecord):
        msg = self.format(record)
        self.Message.emit(msg)

class CustomFormatter(Formatter):
    def format(self, record) -> str:
        level = f"{record.levelname}"
        formatted_msg = f"{level} {record.msg}"
        record.msg = formatted_msg
        return super().format(record)

def initialize_logging(log_name, log_level:_Level = DEBUG):
    log_file = f"[process_name].log"
    logger = getLogger()
    if not logger.handlers:
        fmtter = CustomFormatter("%(asctime)s %(message)s")

        stream_handler = StreamHandler()
        stream_handler.setFormatter(fmtter)

        logger.addHandler(stream_handler)

        file_handler = FileHandler(log_file)
        file_handler.setFormatter(fmtter)

        logger.addHandler(file_handler)

        time.sleep(1) # one second to setup

    logger.setLevel(log_level)
