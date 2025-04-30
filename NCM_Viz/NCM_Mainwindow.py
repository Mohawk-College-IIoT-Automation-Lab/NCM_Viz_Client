import os
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QApplication
from PyQt5.QtCore import QTimer
from .Transform import Size
from .QT_NCM_Status_Lights import StatusWidget
from .QT_NCM_Actions import Actions
from .QT_NCM_Sensors import SensorGraphWidget

from .Mqtt.GenericMqtteLogger.davids_logger import initialize_logging
import logging
from multiprocessing import Event

if os.name != 'nt':
    os.environ["QT_QPA_PLATFORM"] = "xcb" # required for drop down to work

class MainWindow(QMainWindow):

    GRAPH_WIDGET_SIZE = Size(400, 400)

    def __init__(self, log_name:str="Qt", host_name:str="localhost", host_port:int=1883, exit_event:Event=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exit_event = exit_event

        self.setWindowTitle("Main Window")

        initialize_logging(process_name=log_name, broker=host_name, port=host_port)
        logging.debug(f"[Qt] Creating MainWindow")

        
        central_widget = QWidget(self)
        central_v_box_layout = QVBoxLayout(central_widget)

        alarms = StatusWidget(self.statusBar(), log_name=log_name, host_name=host_name, host_port=host_port)
        self.custom_actions = Actions(status_bar=self.statusBar(), log_name=log_name, host_name=host_name, host_port=host_port, parent=self)

        tab_widget = QTabWidget()
        sensor_tab = SensorGraphWidget(self.statusBar(), log_name=log_name, host_name=host_name, host_port=host_port, parent=self)
        sen_control_tab = QWidget()

        self.setCentralWidget(central_widget)

        # Set the layout on the central widge
        tab_widget.setGeometry(0, 0, 500, 500)
        tab_widget.addTab(sensor_tab, "Sensors")
        tab_widget.addTab(sen_control_tab, "SEN Control")

        # Set the layout on the central widget
        central_v_box_layout.addWidget(alarms)
        central_v_box_layout.addWidget(tab_widget)
        central_widget.setLayout(central_v_box_layout)
        
        self.showMaximized()
    
    def closeEvent(self, event):
        logging.info("[QT] Closing windows and issuing exit event set")
        self.exit_event.set()
        event.accept()



        



