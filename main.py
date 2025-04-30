from PyQt5.QtWidgets import QApplication
from NCM_Viz.NCM_Mainwindow import MainWindow
from NI_DAQ import DAQ_Process
import sys

from multiprocessing import set_start_method


app = None
main = None
daq = None

def custom_exit(app: QApplication):
    app.exec_()

    return 0
    
if __name__ == "__main__":

    set_start_method("spawn") # Requird for Py QT on Windows

    app = QApplication(sys.argv)
    main = MainWindow()
    daq = DAQ_Process("DAQ", "10.4.8.5", 1883)

    daq.start()
    
    main.show()
    sys.exit(custom_exit())

