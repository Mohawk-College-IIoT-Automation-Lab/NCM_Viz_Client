from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget
from PyQt5.QtCore import pyqtSlot
from Transform import Size
import os

from m_qt_mould import MouldControlTabWidget
from m_qt_alarms import QAlarmWidget
from m_qt_experiment import QExperimentControlWidget
from m_qt_sensors import SensorGraphWidget

if os.name != 'nt':
    os.environ["QT_QPA_PLATFORM"] = "xcb" # required for drop down to work

class MainWindow(QMainWindow):

    GRAPH_WIDGET_SIZE = Size(400, 400)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Main Window")
        
        central_widget = QWidget(self)
        central_v_box_layout = QVBoxLayout(central_widget)

        alarms = QAlarmWidget()
        experiment_control = QExperimentControlWidget()

        tab_widget = QTabWidget()
        sensor_tab = SensorGraphWidget()
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
        central_v_box_layout.addWidget(experiment_control)
        central_v_box_layout.addWidget(tab_widget)
        central_widget.setLayout(central_v_box_layout)

        sensor_tab.sensor_m_qobject.status_bar_printer.connect(self.status_bar_printer)
        alarms.alarm_m_qobject.status_bar_printer.connect(self.status_bar_printer)
        
        self.showMaximized()

    @pyqtSlot(str)
    def status_bar_printer(self, message):
        self.statusBar().showMessage(message)



        



