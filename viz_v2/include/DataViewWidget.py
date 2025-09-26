from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QTreeView, QVBoxLayout, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class DataViewWidget(QWidget):

    class SensorDataTree(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            _model = QStandardItemModel()
            _model.setHorizontalHeaderLabels(["Key", "Value"])

            # Common Items

            _ll_k = QStandardItem("LL")
            _ll_k.setEditable(False)

            _lq_k = QStandardItem("LQ")
            _lq_k.setEditable(False)

            _rq_k = QStandardItem("RQ")
            _rq_k.setEditable(False)

            _rr_k = QStandardItem("RR")
            _rr_k.setEditable(False)

            # Ultrasonic Sensotrs Items
            _usd_k = QStandardItem("Ultrasonice Sensors")
            _usd_k.setEditable(False)

            self._usd_ll_v = QStandardItem("0")
            self._usd_ll_v.setEditable(False)

            self._usd_lq_v = QStandardItem("0")
            self._usd_lq_v.setEditable(False)

            self._usd_rq_v = QStandardItem("0")
            self._usd_rq_v.setEditable(False)

            self._usd_rr_v = QStandardItem("0")
            self._usd_rr_v.setEditable(False)

            _usd_k.appendRow([_ll_k, self._usd_ll_v])
            _usd_k.appendRow([_lq_k, self._usd_lq_v])
            _usd_k.appendRow([_rq_k, self._usd_rq_v])
            _usd_k.appendRow([_rr_k, self._usd_rr_v])

            # Anemometer Sensors Items
            _anm_k = QStandardItem("Anemometers")
            _anm_k.setEditable(False)

            self._anm_ll_v = QStandardItem("0")
            self._anm_ll_v.setEditable(False)

            self._anm_lq_v = QStandardItem("0")
            self._anm_lq_v.setEditable(False)

            self._anm_rq_v = QStandardItem("0")
            self._anm_rq_v.setEditable(False)

            self._anm_rr_v = QStandardItem("0")
            self._anm_rr_v.setEditable(False)

            _anm_k.appendRow([_ll_k.clone(), self._anm_ll_v])
            _anm_k.appendRow([_lq_k, self._anm_lq_v])
            _anm_k.appendRow([_rq_k, self._anm_rq_v])
            _anm_k.appendRow([_rr_k, self._anm_rr_v])

            _model.appendRow(_usd_k)
            _model.appendRow(_anm_k)

            _tree = QTreeView()
            _tree.setModel(_model)

            _central_v_box = QVBoxLayout()

            _central_v_box.addWidget(_tree)
            self.setLayout(_central_v_box)

    class SenTeleTree(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            _model = QStandardItemModel()
            _model.setHorizontalHeaderLabels(["Key", "Value"])

            _tree = QTreeView()
            _tree.setModel(_model)

            _central_v_box = QVBoxLayout()

            _central_v_box.addWidget(_tree)
            self.setLayout(_central_v_box)

    class SenConfigTree(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            _model = QStandardItemModel()
            _model.setHorizontalHeaderLabels(["Key", "Value"])

            _tree = QTreeView()
            _tree.setModel(_model)

            _central_v_box = QVBoxLayout()

            _central_v_box.addWidget(_tree)
            self.setLayout(_central_v_box)

    def __init__(self, parent=None):
        super().__init__(parent)

        center_h_box = QHBoxLayout()

        self._sensor_tree = DataViewWidget.SensorDataTree()
        self._sen_tele_tree = DataViewWidget.SenTeleTree()
        self._sen_config_tree = DataViewWidget.SenConfigTree()

        center_h_box.addWidget(self._sensor_tree)
        center_h_box.addWidget(self._sen_tele_tree)
        center_h_box.addWidget(self._sen_config_tree)

        self.setLayout(center_h_box)
