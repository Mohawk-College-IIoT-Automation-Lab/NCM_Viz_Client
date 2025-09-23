from re import DEBUG
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QTabWidget, QVBoxLayout, QWidget

from .Logger import initialize_logging
from .Qt.MenuBar import MenuBar
import logging

LOG_LEADER = "QT"


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        window_title = "Nexus Control Module Vizulation Software"
        self.setWindowTitle(window_title)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        initialize_logging(log_name="Qt", log_level=DEBUG, status_bar=self.statusBar())
        logging.debug("Creating MainWindow")

        menu_bar = MenuBar(self)
        self.setMenuBar(menu_bar)

        # replace all w/ custom
        tab_widget = QTabWidget()
        sen_tab_widget = QWidget()
        graph_tab_widget = QWidget()
        data_tab_widget = QWidget()

        tab_widget.setGeometry(0, 0, 500, 500)
        tab_widget.addTab(sen_tab_widget, "SEN")
        tab_widget.addTab(graph_tab_widget, "Graphs")
        tab_widget.addTab(data_tab_widget, "Dataview")

        central_v_box = QVBoxLayout(central_widget)
        central_v_box.addWidget(tab_widget)
        central_widget.setLayout(central_v_box)

        self.showMaximized()
        logging.debug("Maximizaing MainWindow")




