from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget
from QT_Visualizer.Transform import Size
import os

from QT_Visualizer.m_qt_mould import MouldControlTabWidget
from QT_Visualizer.m_qt_alarms import QAlarmWidget
from QT_Visualizer.m_qt_actions import M_ActionsSingleton
from QT_Visualizer.m_qt_sensors import SensorGraphWidget

if os.name != 'nt':
    os.environ["QT_QPA_PLATFORM"] = "xcb" # required for drop down to work

class MainWindow(QMainWindow):

    GRAPH_WIDGET_SIZE = Size(400, 400)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Main Window")
        
        central_widget = QWidget(self)
        central_v_box_layout = QVBoxLayout(central_widget)

        alarms = QAlarmWidget(self.statusBar())
        experiment_control = M_ActionsSingleton(self.statusBar(), self)

        tab_widget = QTabWidget()
        sensor_tab = SensorGraphWidget(self.statusBar())
        mould_control_tab = MouldControlTabWidget()
        sen_control_tab = QWidget()

        self.setCentralWidget(central_widget)

        # Set the layout on the central widge
        tab_widget.setGeometry(0, 0, 500, 500)
        tab_widget.addTab(sensor_tab, "Sensors")
        tab_widget.addTab(mould_control_tab, "Mould Control")
        tab_widget.addTab(sen_control_tab, "SEN Control")

        # Set the layout on the central widget
        central_v_box_layout.addWidget(alarms)
        central_v_box_layout.addWidget(tab_widget)
        central_widget.setLayout(central_v_box_layout)
        
        self.showMaximized()




        



