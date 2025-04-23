from m_qobject import *
from m_qt_graphs import Q2SensorsGraph
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSlot, pyqtSignal

import json
from pydantic import BaseModel

class SensorReadings(BaseModel):
    LL: float
    LQ: float
    RR: float
    RQ: float
    
class SensorData(BaseModel):
    Ultra_Sonic_Distance: SensorReadings
    Anemometer: SensorReadings

class QMqttSensors(M_QObject):

    distance_data_ready = pyqtSignal(float, float, float, float)
    anemometer_data_ready = pyqtSignal(float, float, float, float)

    def __init__(self, host_name:str="localhost", host_port:int=1883, parent=None):
        super().__init__(False, host_name, host_port, parent)

        self.display_data_topic = "NCM/SensorData"

        self.mqtt_client.message_callback_add(self.display_data_topic, self.mqtt_display_callback)
        self.mqtt_client.subscribe(self.display_data_topic)
        
    def mqtt_display_callback(self, client:Client, userdata, message:MQTTMessage):
        try:
            payload = json.load(message.payload.decode())
            sensor_data = SensorData(**payload)

            self.log(f"[MQTT][SensorData] Received data: {sensor_data}")

            self.distance_data_ready.emit(sensor_data.Ultra_Sonic_Distance.LL, sensor_data.Ultra_Sonic_Distance.LQ, sensor_data.Ultra_Sonic_Distance.RQ, sensor_data.Ultra_Sonic_Distance.RR)
            self.anemometer_data_ready.emit(sensor_data.Anemometer.LL, sensor_data.Anemometer.LQ, sensor_data.Anemometer.RQ, sensor_data.Anemometer.RR)
            
        except json.JSONDecodeError:
            self.emit_and_log(f"[MQTT][JSON Error] Loading / decoding error - Data: {message.payload.decode()}")

class SensorGraphWidget(QWidget):

    def __init__(self, parent=None, host_name:str="localhost", host_port:int=1883, **kargs):
        super().__init__(parent, **kargs)

        main_h_box = QHBoxLayout(self)
        left_v_box = QVBoxLayout()
        right_v_box = QVBoxLayout()
        left_h_box = QHBoxLayout()

        self.usd_ll_lq_graph = Q2SensorsGraph(title="USD - Left Mould (LL, LQ)")
        self.usd_rq_rr_graph = Q2SensorsGraph(title="USD - Right Mould (RQ, RR)")
        self.standing_wave_graph = Q2SensorsGraph(title="Stating Wave Height (LL-LQ) (RR-RQ)")

        self.an_ll_lq_graph = Q2SensorsGraph(title="ANM - Left Mould (LL, LQ)")
        self.an_rq_rr_graph = Q2SensorsGraph(title="ANM - Right Mould (RQ, RR)")

        left_h_box.addWidget(self.usd_ll_lq_graph)
        left_h_box.addWidget(self.usd_rq_rr_graph)

        left_v_box.addWidget(self.standing_wave_graph)
        left_v_box.addLayout(left_h_box)

        right_v_box.addWidget(self.an_ll_lq_graph)
        right_v_box.addWidget(self.an_rq_rr_graph)
        
        main_h_box.addLayout(left_v_box)
        main_h_box.addLayout(right_v_box)

        self.setLayout(main_h_box)

        self.sensor_m_qobject = QMqttSensors(host_name=host_name, host_port=host_port)
        self.sensor_m_qobject.distance_data_ready.connect(self.update_usd_plot)
        self.sensor_m_qobject.anemometer_data_ready.connect(self.update_an_plot)
        
        # self.sensor_object.mqtt_connect()

    @pyqtSlot(float, float, float, float)
    def update_usd_plot(self, ll_value:float, lq_value:float, rq_value:float, rr_value:float):
        left_standing_wave = ll_value - lq_value
        right_standing_wave = rr_value - rq_value
        
        self.usd_ll_lq_graph.update_plot(lq_value, ll_value)
        self.usd_rq_rr_graph.update_plot(rq_value, rr_value)
        self.standing_wave_graph.update_plot(left_standing_wave, right_standing_wave)

    @pyqtSlot(float, float, float, float)
    def update_an_plot(self, ll_value:float, lq_value:float, rq_value:float, rr_value:float):
        self.an_ll_lq_graph.update_plot(lq_value, ll_value)
        self.an_rq_rr_graph.update_plot(rq_value, rr_value)