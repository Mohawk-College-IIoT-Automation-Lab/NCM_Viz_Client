import os
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabWidget
from .Transform import Size
from .QT_NCM_Status_Lights import StatusWidget
from Mqtt.actions_mqtt import ActionsMQTT
from .QT_NCM_Sensors import SensorGraphWidget
from .QT_NCM_MenuBar import M_QMenuBar

from Mqtt.GenericMqtteLogger import initialize_logging
import logging
from multiprocessing import Event
from Constants.configs import LoggerConfig

if os.name != 'nt':
    os.environ["QT_QPA_PLATFORM"] = "xcb" # required for drop down to work

class MainWindow(QMainWindow):

    GRAPH_WIDGET_SIZE = Size(400, 400)

    def __init__(self, logger_config:LoggerConfig, exit_event:Event=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exit_event = exit_event

        self.setWindowTitle("Main Window")

        initialize_logging(process_name=logger_config.log_name, broker=logger_config.mqtt_config.host_name, port=logger_config.mqtt_config.host_port)
        logging.debug(f"[Qt] Creating MainWindow")

        actions = ActionsMQTT.get_instance(self.statusBar(), logger_config)

        menu_bar = M_QMenuBar(self.statusBar(), logger_config, self)
        self.setMenuBar(menu_bar)
        
        central_widget = QWidget(self)
        central_v_box_layout = QVBoxLayout(central_widget)

        alarms = StatusWidget(status_bar=self.statusBar(), logger_config=logger_config)

        tab_widget = QTabWidget()
        sensor_tab = SensorGraphWidget(logger_config=logger_config, parent=self)
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


        



