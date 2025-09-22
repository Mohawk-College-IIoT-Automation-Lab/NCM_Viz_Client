from re import A
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QTreeView, QWidget, QHBoxLayout, QVBoxLayout, QStatusBar
from PyQt5.QtCore import pyqtSlot
from typing import List
import json

from Constants.base_models import SensorData, XM430Config, XM430Telemetery
from Constants.configs import LoggerConfig 

def SensorDataModel(sensor_data: SensorData):
    model = QStandardItemModel()

    usd = QStandardItem("Ultrasonic Distance Sensors")
    usd.setEditable(False)

    anm = QStandardItem("Anemometer Sensors")
    anm.setEditable(False)

    sw = QStandardItem("Standing Wave")
    sw.setEditable(False)

    usd_ll = QStandardItem(f"LL: {sensor_data.Ultra_Sonic_Distance.LL}")
    usd_ll.setEditable(False)
    usd_lq = QStandardItem(f"LQ: {sensor_data.Ultra_Sonic_Distance.LQ}")
    usd_lq.setEditable(False)

    usd_rr = QStandardItem(f"RR: {sensor_data.Ultra_Sonic_Distance.RR}")
    usd_rr.setEditable(False)
    usd_rq = QStandardItem(f"RQ: {sensor_data.Ultra_Sonic_Distance.RQ}")
    usd_rq.setEditable(False)

    anm_ll = QStandardItem(f"LL: {sensor_data.Anemometer.LL}")
    anm_ll.setEditable(False)
    anm_lq = QStandardItem(f"LQ: {sensor_data.Anemometer.LQ}")
    anm_lq.setEditable(False)

    anm_rr = QStandardItem(f"RR: {sensor_data.Anemometer.RR}")
    anm_rr.setEditable(False)
    anm_rq = QStandardItem(f"RQ: {sensor_data.Anemometer.RQ}")
    anm_rq.setEditable(False)

    sw_left = QStandardItem(f"Left: {sensor_data.Standing_Wave.Left}")
    sw_left.setEditable(False)
    sw_right = QStandardItem(f"Right: {sensor_data.Standing_Wave.Right}")
    sw_right.setEditable(False)

    usd.appendRow(usd_ll)
    usd.appendRow(usd_lq)
    usd.appendRow(usd_rq)
    usd.appendRow(usd_rr)

    anm.appendRow(anm_ll)
    anm.appendRow(anm_lq)
    anm.appendRow(anm_rq)
    anm.appendRow(anm_rr)

    sw.appendRow(sw_left)
    sw.appendRow(sw_right)

    model.appendRow(usd)
    model.appendRow(anm)
    model.appendRow(sw)

    return model

def TelemeteryModel(tele : XM430Telemetery):
    model = QStandardItemModel()


    return model 

def ConfigModel(config : XM430Config):
    model = QStandardItemModel()

    return model

class DataVizWidget(QWidget):

    def __init__(self, logging_config:LoggerConfig, parent=None, **kargs):
        super().__init__(parent, **kargs)

        main_h_box = QHBoxLayout(self)
        sen1_v_box = QVBoxLayout()
        sen2_v_box = QVBoxLayout()
        
        
        self.sensor_data_treeview = QTreeView()
        self.sen1_tele_treeview = QTreeView()
        self.sen2_tele_treeview = QTreeView()
        self.sen1_config_treeview = QTreeView()
        self.sen2_config_treeview = QTreeView()

        main_h_box.addWidget(self.sensor_data_treeview)
        
        sen1_v_box.addWidget(self.sen1_tele_treeview)
        sen1_v_box.addWidget(self.sen1_config_treeview)

        sen2_v_box.addWidget(self.sen2_tele_treeview)
        sen2_v_box.addWidget(self.sen2_config_treeview)

        main_h_box.addLayout(sen1_v_box)
        main_h_box.addLayout(sen2_v_box)

    
    @pyqtSlot()
    def sensors_slot(self, sensor_data: SensorData):
        self.sensor_data_treeview.setModel(SensorDataModel(sensor_data))

    @pyqtSlot()
    def sen1_tele_slot(self, tele: XM430Telemetery):
        self.sen1_tele_treeview.setModel(TelemeteryModel(tele))

    @pyqtSlot()
    def sen2_tele_slot(self, tele: XM430Telemetery):
        self.sen2_tele_treeview.setModel(TelemeteryModel(tele))

    @pyqtSlot()
    def sen1_config_slot(self, config : XM430Config):
        self.sen1_config_treeview.setModel(ConfigModel(config))

    @pyqtSlot()
    def sen2_config_slot(self, config:XM430Config):
        self.sen2_config_treeview.setModel(ConfigModel(config))

