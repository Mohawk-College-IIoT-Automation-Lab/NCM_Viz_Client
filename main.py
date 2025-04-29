from PyQt5.QtWidgets import QApplication
from NCM_Viz.NCM_Mainwindow import MainWindow
from NI_DAQ import DAQ_Process
import sys

daq_process = DAQ_Process()

app = None
main = None

def custom_exit(app: QApplication):
    app.exec_()
    daq_process.stop()

    app = QApplication(sys.argv)
    main = MainWindow()
    
    main.show()
    sys.exit(custom_exit(app))