from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget
from custom_qt_widgets import *
from Transform import Size
import sys, os, PyQt5
from Mqtt import *

if os.name != 'nt':
    os.environ["QT_QPA_PLATFORM"] = "xcb" # required for drop down to work

class MainWindow(QMainWindow):

    GRAPH_WIDGET_SIZE = Size(400, 400)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Main Window")

        self.showMaximized()

        self.central_widget = QWidget(self)
        
        self.central_v_box_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.experiment_tab = QWidget()
        self.control_tab = QWidget()

        self.graphs = QCustomGraphsWidget(self.experiment_tab)
        self.alarms = QAlarmWidget()

        self.mqtt_sensor_object = QMqttSensors("10.4.5.8", 1883)
        self.mqtt_sensor_object.distance_data_ready.connect(self.graphs.update_plot)


        self.__setup_window__()

    def __setup_window__(self):
        self.setCentralWidget(self.central_widget)

        # Set the layout on the central widge
        self.tab_widget.setGeometry(0, 0, 500, 500)
        self.tab_widget.addTab(self.experiment_tab, "Experiment")
        self.tab_widget.addTab(self.control_tab, "Control")

        self.central_v_box_layout.addWidget(self.alarms)
        self.central_v_box_layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.central_v_box_layout)



        


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
