from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QTreeView, QVBoxLayout, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from .DataStructures import SensorData, SenConfigModel, SenTelemetry


class DataViewWidget(QWidget):

    class SensorDataTree(QWidget):
        def __init__(self, parent=None, timer_int:int = 100):
            super().__init__(parent)

            _model = QStandardItemModel()
            _model.setHorizontalHeaderLabels(["Key", "Value"])


            self._t_counter = 0
            self._t_int = timer_int
            self._timer = QTimer(self)
            self._timer.setInterval(timer_int)
            self._timer.timeout.connect(self.UpdateTimer)

            _time_k = QStandardItem("Elapsed from Rx")
            _time_k.setEditable(False)
            self._time_v = QStandardItem(str(self._t_counter))
            self._time_v.setEditable(False)

            # Ultrasonic Sensotrs Items
            _usd_k = QStandardItem("Ultrasonice Sensors")
            _usd_k.setEditable(False)

            _usd_ll_k = QStandardItem("LL")
            _usd_ll_k.setEditable(False)
            self._usd_ll_v = QStandardItem("0")
            self._usd_ll_v.setEditable(False)

            _usd_lq_k = QStandardItem("LQ")
            _usd_lq_k.setEditable(False)
            self._usd_lq_v = QStandardItem("0")
            self._usd_lq_v.setEditable(False)

            _usd_rq_k = QStandardItem("RQ")
            _usd_rq_k.setEditable(False)
            self._usd_rq_v = QStandardItem("0")
            self._usd_rq_v.setEditable(False)

            _usd_rr_k = QStandardItem("RR")
            _usd_rr_k.setEditable(False)
            self._usd_rr_v = QStandardItem("0")
            self._usd_rr_v.setEditable(False)

            _usd_k.appendRow([_usd_ll_k, self._usd_ll_v])
            _usd_k.appendRow([_usd_lq_k, self._usd_lq_v])
            _usd_k.appendRow([_usd_rq_k, self._usd_rq_v])
            _usd_k.appendRow([_usd_rr_k, self._usd_rr_v])

            # Anemometer Sensors Items
            _anm_k = QStandardItem("Anemometers")
            _anm_k.setEditable(False)

            _anm_ll_k = QStandardItem("LL")
            _anm_ll_k.setEditable(False)
            self._anm_ll_v = QStandardItem("0")
            self._anm_ll_v.setEditable(False)

            _anm_lq_k = QStandardItem("LQ")
            _anm_lq_k.setEditable(False)
            self._anm_lq_v = QStandardItem("0")
            self._anm_lq_v.setEditable(False)

            _anm_rq_k = QStandardItem("RQ")
            _anm_rq_k.setEditable(False)
            self._anm_rq_v = QStandardItem("0")
            self._anm_rq_v.setEditable(False)

            _anm_rr_k = QStandardItem("RR")
            _anm_rr_k.setEditable(False)
            self._anm_rr_v = QStandardItem("0")
            self._anm_rr_v.setEditable(False)

            _anm_k.appendRow([_anm_ll_k, self._anm_ll_v])
            _anm_k.appendRow([_anm_lq_k, self._anm_lq_v])
            _anm_k.appendRow([_anm_rq_k, self._anm_rq_v])
            _anm_k.appendRow([_anm_rr_k, self._anm_rr_v])

            # Standing wave Items
            _sw_k = QStandardItem("Standing Wave")

            _sw_left_k = QStandardItem("Left")
            _sw_left_k.setEditable(False)
            self._sw_left_v = QStandardItem("0")
            self._sw_left_v.setEditable(False)

            _sw_right_k = QStandardItem("Right")
            _sw_right_k.setEditable(False)
            self._sw_right_v = QStandardItem("0")
            self._sw_right_v.setEditable(False)

            _sw_k.appendRow([_sw_left_k, self._sw_left_v])
            _sw_k.appendRow([_sw_right_k, self._sw_right_v])

            _model.appendRow([_time_k, self._time_v])
            _model.appendRow(_usd_k)
            _model.appendRow(_anm_k)
            _model.appendRow(_sw_k)

            _tree = QTreeView()
            _tree.setModel(_model)

            _central_v_box = QVBoxLayout()

            _central_v_box.addWidget(_tree)
            self.setLayout(_central_v_box)

            self._timer.start()

        @pyqtSlot()
        def UpdateTimer(self):
            self._t_counter += self._t_int
            self._time_v.setText(f"{self._t_counter} ms")

        @pyqtSlot()
        def UpdateTree(self, data: SensorData):

            self._timer.stop()
            self._t_counter = 0

            self._usd_ll_v.setText(str(data.Ultra_Sonic_Distance.LL))
            self._usd_lq_v.setText(str(data.Ultra_Sonic_Distance.LQ))
            self._usd_rq_v.setText(str(data.Ultra_Sonic_Distance.RQ))
            self._usd_rr_v.setText(str(data.Ultra_Sonic_Distance.RR))

            self._anm_ll_v.setText(str(data.Anemometer.LL))
            self._anm_lq_v.setText(str(data.Anemometer.LQ))
            self._anm_rq_v.setText(str(data.Anemometer.RQ))
            self._anm_rr_v.setText(str(data.Anemometer.RR))

            self._sw_left_v.setText(str(data.Standing_Wave.Left))
            self._sw_right_v.setText(str(data.Standing_Wave.Right))

            self._timer.start()

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
