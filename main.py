from PyQt5.QtWidgets import QApplication
from NCM_Viz.NCM_Mainwindow import MainWindow
from NI_DAQ.DAQ import DAQConfig, DAQ, initialize_logging
import logging
import sys, signal

from multiprocessing import set_start_method, Event, Process


app = None
main = None
stop_event = None
daq_config = DAQConfig(log_name="DAQ", host_name="10.4.8.5", host_port=1883)


def gui_process_callback(exit_event: Event, log_name:str="Qt", host_name:str="localhost", host_port:int=1883):
    def handle_sigint(*args):
        print("Ctrl+C detected in GUI. Signaling parent...")
        exit_event.set()
        app.quit()

    signal.signal(signal.SIGINT, handle_sigint)

    app = QApplication(sys.argv)
    window = MainWindow(log_name=log_name, host_name=host_name, host_port=host_port, exit_event=exit_event)
    window.show()

    sys.exit(app.exec_())


def custom_exit():
    stop_event.set()
    logging.debug("[Main] Exitting fom life")
    return 0

if __name__ == "__main__":

    set_start_method("spawn") # Requird for Py QT on Windows

    host = str("10.4.8.5")
    port = 1883

    initialize_logging(process_name="Main", broker=host, port=port)

    logging.debug(f"[Main] Main initialized. ")
    

    stop_event = Event()

    logging.debug(f"[Main] Starting DAQ Process")
    daq_process = Process(target=DAQ.run, args=(daq_config,stop_event))
    daq_process.start()

    
    logging.debug(f"[Main] Starting QApp and Mainwindow")
    gui_process = Process(target=gui_process_callback, args=(stop_event, "Qt", host, port))
    gui_process.start()

    stop_event.wait()

    daq_process.join()
    gui_process.join()



