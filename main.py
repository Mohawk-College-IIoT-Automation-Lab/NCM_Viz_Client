from PyQt5.QtWidgets import QApplication
from NCM_Viz.NCM_Mainwindow import MainWindow
from NCM_Viz.Mqtt.GenericMqtteLogger import initialize_logging
from Constants import LoggerConfig, MQTTConfig
import logging
import sys, signal

from multiprocessing import set_start_method, Event, Process

stop_event = Event()
app = QApplication(sys.argv)

def handle_sigint(*args):
    stop_event.set()
    app.quit()
    

if __name__ == "__main__":

    set_start_method("spawn") # Requird for Py QT on Windows

    mqtt_config = MQTTConfig()

    initialize_logging(process_name="Main", broker=mqtt_config.host_name, port=mqtt_config.host_port)

    logging.debug(f"[Main] Main initialized. ")
    stop_event = Event()

    logging.debug(f"[Main] Starting QApp and Mainwindow")
    gui_logger = LoggerConfig(log_name="Qt", mqtt_config=mqtt_config)

    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)
    signal.signal(signal.SIGHUP, handle_sigint)

    window = MainWindow(logger_config=gui_logger, exit_event=stop_event)

    window.show()
    sys.exit(app.exec_())




