from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, QTabWidget
from PyQt5.QtCore import QRect
from PyQt5.QtChart import *
from custom_labels import AlarmLabel
from dimensions import Dimension
import sys, os


class MainWindow(QMainWindow):

    WINDOW_DIMS = Dimension(0, 0, 800, 600)
    CENTRAL_WIDGET_DIMS = Dimension(10, 10, 780, 50)
    ALARM_LABEL_DIMS = Dimension(0, 0, 50, 50)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("main_window")
        self.setWindowTitle("Main Window")

        self.setFixedSize(MainWindow.WINDOW_DIMS.w, MainWindow.WINDOW_DIMS.h)

        self.central_widget = QWidget(self)

        self.central_widget.setGeometry(
            QRect(
                MainWindow.CENTRAL_WIDGET_DIMS.x, 
                MainWindow.CENTRAL_WIDGET_DIMS.y, 
                MainWindow.CENTRAL_WIDGET_DIMS.w, 
                MainWindow.CENTRAL_WIDGET_DIMS.h))
        
        self.setCentralWidget(self.central_widget)
        
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

        for label in self.labels:
            self.alarm_h_box_layout.addWidget(label)

        # Set the layout on the central widget
        self.central_v_box_layout.addLayout(self.alarm_h_box_layout)
        
        self.experiment_tab = QWidget()
        self.experiment_tab.setObjectName("experiment_tab")
        
        self.chart_grid_box_layout = QGridLayout(self.experiment_tab)

        self.distance_chart_1 = QChart()
        self.distance_chart_view_1 = QChartView(self.distance_chart_1)

        self.distance_chart_2 = QChart()
        self.distance_chart_view_2 = QChartView(self.distance_chart_2)

        self.chart_grid_box_layout.addWidget(self.distance_chart_view_1, 0, 0)
        self.chart_grid_box_layout.addWidget(self.distance_chart_view_2, 0, 1)

        self.control_tab = QWidget()
        self.control_tab.setObjectName("control_tab")

        self.tab_widget = QTabWidget()
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
