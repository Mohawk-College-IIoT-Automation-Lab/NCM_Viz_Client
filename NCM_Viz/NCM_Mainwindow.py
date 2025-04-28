import os
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget
from .Transform import Size
from .QT_NCM_Status_Lights import StatusWidget
from .QT_NCM_Actions import M_ActionsSingleton
from .QT_NCM_Sensors import SensorGraphWidget

from .Mqtt.GenericMqtteLogger import Logger

if os.name != 'nt':
    os.environ["QT_QPA_PLATFORM"] = "xcb" # required for drop down to work

class MainWindow(QMainWindow):

    GRAPH_WIDGET_SIZE = Size(400, 400)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logger = Logger("qt_log")

        self.setWindowTitle("Main Window")
        
        central_widget = QWidget(self)
        central_v_box_layout = QVBoxLayout(central_widget)

        alarms = StatusWidget(self.statusBar(), logger=logger)
        self.custom_actions = M_ActionsSingleton(status_bar=self.statusBar(), logger=logger, parent=self)

        tab_widget = QTabWidget()
        sensor_tab = SensorGraphWidget(self.statusBar(), logger=logger, parent=self)
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




        



