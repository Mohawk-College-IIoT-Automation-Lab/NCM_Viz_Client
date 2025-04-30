from PyQt5.QtWidgets import QApplication
from NCM_Viz.NCM_Mainwindow import MainWindow
from NI_DAQ.DAQ import DAQ, initialize_logging
from Constants import DAQConfig, LoggerConfig, MQTTConfig
import logging
import sys, signal

from multiprocessing import set_start_method, Event, Process


def gui_process_callback(logger_config:LoggerConfig, exit_event: Event):
    def handle_sigint(*args):
        print("Ctrl+C detected in GUI. Signaling parent...")
        exit_event.set()
        app.quit()

    signal.signal(signal.SIGINT, handle_sigint)

    app = QApplication(sys.argv)
    window = MainWindow(logger_config=logger_config, exit_event=exit_event)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    set_start_method("spawn") # Requird for Py QT on Windows

    mqtt_config = MQTTConfig(host_name="10.4.8.5", host_port=1883)

    initialize_logging(process_name="Main", broker=mqtt_config.host_name, port=mqtt_config.host_port)

    logging.debug(f"[Main] Main initialized. ")
    stop_event = Event()

    logging.debug(f"[Main] Starting DAQ Process")
    daq_logger = LoggerConfig(log_name="DAQ", mqtt_config=mqtt_config)
    daq_config = DAQConfig(log_config=daq_logger, mqtt_config=mqtt_config)
    daq_process = Process(target=DAQ.run, args=(daq_config,stop_event))
    daq_process.start()

    
    logging.debug(f"[Main] Starting QApp and Mainwindow")
    gui_logger = LoggerConfig(log_name="Qt", mqtt_config=mqtt_config)
    gui_process = Process(target=gui_process_callback, args=(gui_logger, stop_event))
    gui_process.start()

    stop_event.wait()

    daq_process.join()
    gui_process.join()



