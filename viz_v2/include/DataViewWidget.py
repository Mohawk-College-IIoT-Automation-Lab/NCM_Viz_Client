from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class DataViewWidget(QWidget):

    class SensorDataTree(QWidget):
        def __init__(self, parent = None):
            super().__init__(parent)


    class SenTeleTree(QWidget):
        def __init__(self, parent = None):
            super().__init__(parent)
    
    class SenConfigTree(QWidget):
        def __init__(self, parent = None):
            super().__init__(parent)


    def __init__(self, parent = None):
        super().__init__(parent)

        center_h_box = QHBoxLayout()

        self._sensor_tree = DataViewWidget.SensorDataTree()
        self._sen_tele_tree = DataViewWidget.SenTeleTree()
        self._sen_config_tree = DataViewWidget.SenConfigTree()

        center_h_box.addWidget(self._sensor_tree)
        center_h_box.addWidget(self._sen_tele_tree)
        center_h_box.addWidget(self._sen_config_tree)

        self.setLayout(center_h_box)


