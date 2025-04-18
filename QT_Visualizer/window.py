from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget
from custom_qt import AlarmLabel, QCustomGraphsWidget
from Transform import Size
import sys, os, PyQt5
from Mqtt import QMqttObject

class MainWindow(QMainWindow):

    GRAPH_WIDGET_SIZE = Size(400, 400)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("main_window")
        self.setWindowTitle("Main Window")

        self.showMaximized()

        self.central_widget = QWidget(self)
        
        # Create a horizontal layout
        self.alarm_h_box_layout = QHBoxLayout()
        self.central_v_box_layout = QVBoxLayout(self.central_widget)

        # Create and add labels to the layout
        self.labels = [
            AlarmLabel("Alarm 1"),
            AlarmLabel("Alarm 2"),
            AlarmLabel("Alarm 3"),
            AlarmLabel("Alarm 4")
        ]

        self.tab_widget = QTabWidget()
        self.experiment_tab = QWidget()
        self.control_tab = QWidget()

        self.graphs = QCustomGraphsWidget(self.experiment_tab)

        self.mqtt_client = QMqttObject("10.4.5.8", 1883)
        self.mqtt_client.distance_data_ready.connect(self.graphs.update_plot)


        self.__setup_window__()

    def __setup_window__(self):
        self.setCentralWidget(self.central_widget)

        for label in self.labels:
            self.alarm_h_box_layout.addWidget(label)

        # Set the layout on the central widget
        self.central_v_box_layout.addLayout(self.alarm_h_box_layout)

        self.experiment_tab.setObjectName("experiment_tab")
        self.control_tab.setObjectName("control_tab")

        self.tab_widget.setObjectName("tab_widget")
        self.tab_widget.setGeometry(0, 0, 500, 500)
        self.tab_widget.addTab(self.experiment_tab, "Experiment")
        self.tab_widget.addTab(self.control_tab, "Control")

        self.central_v_box_layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.central_v_box_layout)



        


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
