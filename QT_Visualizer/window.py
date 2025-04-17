import PyQt5.QtChart
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, QTabWidget
from PyQt5.QtCore import QRect, QDateTime, Qt, QPointF
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from custom_qt import AlarmLabel, DistanceGraph
from dimensions import Dimension
import sys, os, PyQt5


class MainWindow(QMainWindow):

    CENTRAL_WIDGET_DIMS = Dimension(10, 10, 780, 50)
    ALARM_LABEL_DIMS = Dimension(0, 0, 50, 50)
    GRAPH_WIDGET_DIMS = Dimension(0, 0, 400, 400)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("main_window")
        self.setWindowTitle("Main Window")

        # self.setFixedSize(MainWindow.WINDOW_DIMS.w, MainWindow.WINDOW_DIMS.h)
        self.showMaximized()

        self.central_widget = QWidget(self)
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

        self.left_dist_graph = DistanceGraph(isLeft=True)
        self.left_dist_graph.setFixedSize(MainWindow.GRAPH_WIDGET_DIMS.w, MainWindow.GRAPH_WIDGET_DIMS.h)

        self.right_dist_graph = DistanceGraph(isLeft=True)
        self.right_dist_graph.setFixedSize(MainWindow.GRAPH_WIDGET_DIMS.w, MainWindow.GRAPH_WIDGET_DIMS.h)

        self.right_dist_graph1 = DistanceGraph(isLeft=True)
        self.right_dist_graph1.setFixedSize(MainWindow.GRAPH_WIDGET_DIMS.w, MainWindow.GRAPH_WIDGET_DIMS.h)

        self.experiment_tab_v_box_layout = QVBoxLayout(self.experiment_tab)

        self.top_graph_h_box_layout = QHBoxLayout()
        self.top_graph_h_box_layout.setContentsMargins(5, 20, 20, 5)
        self.top_graph_h_box_layout.addWidget(self.left_dist_graph)
        self.top_graph_h_box_layout.addWidget(self.right_dist_graph)

        self.experiment_tab_v_box_layout.addLayout(self.top_graph_h_box_layout)
        self.experiment_tab_v_box_layout.addWidget(self.right_dist_graph1)


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
