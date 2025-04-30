from PyQt5.QtWidgets import QApplication
from NCM_Viz.NCM_Mainwindow import MainWindow
from NI_DAQ.DAQ import DAQConfig, DAQ, Logger
import sys

from multiprocessing import set_start_method, Event, Process


app = None
main = None
stop_event = None
daq_config = DAQConfig(host_name="10.4.8.5", host_port=1883)

def custom_exit():
    app.exec_()
    stop_event.set()
    return 0
    
if __name__ == "__main__":

    set_start_method("spawn") # Requird for Py QT on Windows
    

    stop_event = Event()

    daq_process = Process(target=DAQ.run, args=(daq_config,stop_event))
    daq_process.start()

    app = QApplication(sys.argv)
    main = MainWindow()

    main.show()
    sys.exit(custom_exit())

