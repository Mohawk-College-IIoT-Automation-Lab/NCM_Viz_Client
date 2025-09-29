from PyQt5.QtCore import  pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QTreeView, QVBoxLayout, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from .Mqtt import MqttClient
from .DataStructures import PID, Limits, SensorData, SenConfigModel, SenTelemetry, BaseTelemetry


class DataViewWidget(QWidget):
    class SensorDataTree(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            _model = QStandardItemModel()
            _model.setHorizontalHeaderLabels(["Key", "Value"])

            _con_k = QStandardItem("Connected")
            _con_k.setEditable(False)
            self._con_v = QStandardItem(str(False))
            self._con_v.setEditable(False)

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

            _anm_k.appendRow([QStandardItem("LL"), self._anm_ll_v])
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

            _model.appendRow([_con_k, self._con_v])
            _model.appendRow(_usd_k)
            _model.appendRow(_anm_k)
            _model.appendRow(_sw_k)

            _tree = QTreeView()
            _tree.setModel(_model)

            _central_v_box = QVBoxLayout()

            _central_v_box.addWidget(_tree)
            self.setLayout(_central_v_box)

        @pyqtSlot(bool)
        def UpdateCon(self, con: bool):
            self._con_v.setText(f"{con}")

        @pyqtSlot(SensorData)
        def UpdateTree(self, data: SensorData):
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

    class SenTeleTree(QWidget):
        class SenItem(QStandardItem):
            class TeleItem(QStandardItem):
                def __init__(self, label:str = "Tele"):
                    super().__init__(label)
                    
                    _position_k = QStandardItem("position")
                    _position_k.setEditable(False)
                    self._position_v = QStandardItem("0")
                    self._position_v.setEditable(False)

                    _velocity_k = QStandardItem("velocity")
                    _velocity_k.setEditable(False)
                    self._velocity_v = QStandardItem("0")
                    self._velocity_v.setEditable(False)

                    _pwm_k = QStandardItem("pwm")
                    _pwm_k.setEditable(False)
                    self._pwm_v = QStandardItem("0")
                    self._pwm_v.setEditable(False)
                    
                    _current_k = QStandardItem("current")
                    _current_k.setEditable(False)
                    self._current_v = QStandardItem("0")
                    self._current_v.setEditable(False)

                    _percent_k = QStandardItem("percent")
                    _percent_k.setEditable(False)
                    self._percent_v = QStandardItem("0 %")
                    self._percent_v.setEditable(False)

                    _mm_k = QStandardItem("mm")
                    _mm_k.setEditable(False)
                    self._mm_v = QStandardItem("0 mm")
                    self._mm_v.setEditable(False)

                    self.appendRow([_position_k, self._position_v])
                    self.appendRow([_velocity_k, self._velocity_v])
                    self.appendRow([_pwm_k, self._pwm_v])
                    self.appendRow([_current_k, self._current_v])
                    self.appendRow([_percent_k, self._percent_v])
                    self.appendRow((_mm_k, self._mm_v))

                @pyqtSlot(BaseTelemetry)
                def UpadteItems(self, data: BaseTelemetry):
                    self._position_v.setText(str(data.position))
                    self._velocity_v.setText(str(data.velocity))
                    self._current_v.setText(str(data.current))
                    self._pwm_v.setText(str(data.pwm))
                    self._percent_v.setText(f"{data.percent} %")
                    self._mm_v.setText(f"{data.mm} mm")

            def __init__(self, label:str = "Sen"):
                super().__init__(label)

                _con_k = QStandardItem("Connection")
                _con_k.setEditable(False)
                self._con_v = QStandardItem(str(False))
                self._con_v.setEditable(False)

                _moving_k = QStandardItem("Moving")
                _moving_k.setEditable(False)
                self._moving_v = QStandardItem("0")
                self._moving_v.setEditable(False)

                _move_stat_k = QStandardItem("Moving Status")
                _move_stat_k.setEditable(False)
                self._move_stat_v = QStandardItem("0")
                self._move_stat_v.setEditable(False)

                _in_v_k = QStandardItem("Input Voltage")
                _in_v_k.setEditable(False)
                self._in_v_v = QStandardItem(0)
                self._in_v_v.setEditable(False)

                _temp_k = QStandardItem("Temperature")
                _temp_k.setEditable(False)
                self._temp_v = QStandardItem(0)
                self._temp_v.setEditable(False)

                self._pres_tele_v = self.TeleItem("Present Tele")
                self._pres_tele_v.setEditable(False)

                self._goal_tele_v = self.TeleItem("Goal Tele")
                self._goal_tele_v.setEditable(False)

                _v_traj = QStandardItem("Velocity Traj.")
                _v_traj.setEditable(False)
                self._v_traj_v = QStandardItem("0")
                self._v_traj_v.setEditable(False)

                _p_traj = QStandardItem("Position Traj.")
                _p_traj.setEditable(False)
                self._p_traj_v = QStandardItem("0")
                self._p_traj_v.setEditable(False)


                self.appendRow([_con_k, self._con_v])
                self.appendRow([_moving_k, self._moving_v])
                self.appendRow([_move_stat_k, self._move_stat_v])
                self.appendRow([_in_v_k, self._in_v_v])
                self.appendRow([_temp_k, self._temp_v])
                self.appendRow(self._pres_tele_v)
                self.appendRow(self._goal_tele_v)
                self.appendRow([_v_traj, self._v_traj_v])
                self.appendRow([_p_traj, self._p_traj_v])

            @pyqtSlot(bool)
            def UpdateCon(self, con:bool):
                self._con_v.setText(f"{con}")
            
            @pyqtSlot(SenTelemetry)
            def UpadteItems(self, data: SenTelemetry):
                self._moving_v.setText(str(data.moving))
                self._move_stat_v.setText(str(data.moving_status))
                self._temp_v.setText(str(data.present_temp))
                self._in_v_v.setText(str(data.present_input_voltage))

                self._pres_tele_v.UpadteItems(data.present_telemetry)
                self._goal_tele_v.UpadteItems(data.goal_telemetry)

                self._v_traj_v.setText(str(data.velocity_trajectory))
                self._p_traj_v.setText(str(data.position_trajectory))

        def __init__(self, parent=None):
            super().__init__(parent)

            _model = QStandardItemModel()
            _model.setHorizontalHeaderLabels(["Key", "Value"])

            # Left Sen 
            self._left_port_v = self.SenItem("Left Port")
            self._left_port_v.setEditable(False)

            # Right Sen 
            self._right_port_v = self.SenItem("Right Port")
            self._right_port_v.setEditable(False)

            _model.appendRow(self._left_port_v)
            _model.appendRow(self._right_port_v)

            _tree = QTreeView()
            _tree.setModel(_model)

            _central_v_box = QVBoxLayout()

            _central_v_box.addWidget(_tree)
            self.setLayout(_central_v_box)

        @pyqtSlot(SenTelemetry)
        def UpdateLeft(self, left: SenTelemetry):
            self._left_port_v.UpadteItems(left)

        @pyqtSlot(SenTelemetry)
        def UpdateRight(self, right: SenTelemetry):
            self._right_port_v.UpadteItems(right)

        @pyqtSlot(bool)
        def LeftCon(self, con: bool):
            self._left_port_v.UpdateCon(con)

        @pyqtSlot(bool)
        def RightCon(self, con: bool):
            self._right_port_v.UpdateCon(con)


    class SenConfigTree(QWidget):
        class SenConfigItem(QStandardItem):
            class LimitItem(QStandardItem):
                def __init__(self, label:str = "Limit", min:int = 0 , max:int = 0):
                    super().__init__(label)

                    _min_k = QStandardItem("Min")
                    _min_k.setEditable(False)
                    self._min_v = QStandardItem(str(min))
                    self._min_v.setEditable(False)

                    _max_k = QStandardItem("Max")
                    _max_k.setEditable(False)
                    self._max_v = QStandardItem(str(max))
                    self._max_v.setEditable(False)

                    self.appendRow([_min_k, self._min_v])
                    self.appendRow([_max_k, self._max_v])

                @pyqtSlot(Limits)
                def UpdateLimit(self, limit: Limits):
                    self._min_v.setText(str(limit.min))
                    self._max_v.setText(str(limit.max))

            class PIDItem(QStandardItem):
                def __init__(self, label:str= "PID", p:int = 0, i:int = 0, d:int = 0):
                    super().__init__(label)

                    _p_k = QStandardItem("P")
                    _p_k.setEditable(False)
                    self._p_v = QStandardItem(str(p))
                    self._p_v.setEditable(False)

                    _i_k = QStandardItem("I")
                    _i_k.setEditable(False)
                    self._i_v = QStandardItem(str(i))
                    self._i_v.setEditable(False)

                    _d_k = QStandardItem("D")
                    _d_k.setEditable(False)
                    self._d_v = QStandardItem(str(d))
                    self._d_v.setEditable(False)

                    self.appendRow([_p_k, self._p_v])
                    self.appendRow([_i_k, self._i_v])
                    self.appendRow([_d_k, self._d_v])

                @pyqtSlot(PID)
                def UpdatePID(self, pid: PID):
                    self._p_v.setText(str(pid.P))
                    self._i_v.setText(str(pid.I))
                    self._d_v.setText(str(pid.D))

            def __init__(self, label:str = "Config"):
                super().__init__(label)

                _port_k = QStandardItem("Uart Port")
                _port_k.setEditable(False)
                self._port_v = QStandardItem("/")
                self._port_v.setEditable(False)

                _id_k = QStandardItem("Id")
                _id_k.setEditable(False)
                self._id_v = QStandardItem("0")
                self._id_v.setEditable(False)

                _baud_k = QStandardItem("Baud")
                _baud_k.setEditable(False)
                self._baud_v = QStandardItem("0")
                self._baud_v.setEditable(False)

                _d_mode_k = QStandardItem("Drive Mode")
                _d_mode_k.setEditable(False)
                self._d_mode_v = QStandardItem("0")
                self._d_mode_v.setEditable(False)

                _op_mode = QStandardItem("Op Mode")
                _op_mode.setEditable(False)
                self._op_mode_v = QStandardItem("0")
                self._op_mode_v.setEditable(False)

                _move_thresh_k = QStandardItem("Moving Threshold")
                _move_thresh_k.setEditable(False)
                self._mv_th_v = QStandardItem("0")
                self._mv_th_v.setEditable(False)

                _t_limit_k = QStandardItem("Temp Limit")
                _t_limit_k.setEditable(False)
                self._t_limit_v = QStandardItem("0")
                self._t_limit_v.setEditable(False)

                self._v_lim = self.LimitItem("Voltage Limits")

                _pwm_lim_k = QStandardItem("PWM Limit")
                _pwm_lim_k.setEditable(False)
                self._pwm_lim_v = QStandardItem("0")
                self._pwm_lim_v.setEditable(False)

                _curr_lim_k = QStandardItem("Current Limit")
                _curr_lim_k.setEditable(False)
                self._curr_lim_v = QStandardItem("0")
                self._curr_lim_v.setEditable(False)

                _vel_lim = QStandardItem("Velocity Limit")
                _vel_lim.setEditable(False)
                self._vel_lim_v = QStandardItem("0")
                self._vel_lim_v.setEditable(False)

                self._pos_lim = self.LimitItem("Position Limits")

                self._v_pid = self.PIDItem("Velocity PID")
                self._p_pid = self.PIDItem("Position PID")

                _ff1 = QStandardItem("FF Gain 1")
                _ff1.setEditable(False)
                self._ff1_v = QStandardItem("0")
                self._ff1_v.setEditable(False)

                _ff2 = QStandardItem("FF Gain 2")
                _ff2.setEditable(False)
                self._ff2_v = QStandardItem("0")
                self._ff2_v.setEditable(False)

                _map_k = QStandardItem("Mappings")
                _map_k.setEditable(False)
                self._map_v = QStandardItem("[ ]")
                self._map_v.setEditable(False)

                _dir_k = QStandardItem("Direction")
                _dir_k.setEditable(False)
                self._dir_v = QStandardItem("0")
                self._dir_v.setEditable(False)

                self.appendRow([_port_k, self._port_v])
                self.appendRow([_id_k, self._id_v])
                self.appendRow([_baud_k, self._baud_v])
                self.appendRow([_d_mode_k, self._d_mode_v])
                self.appendRow([_op_mode, self._op_mode_v])
                self.appendRow([_move_thresh_k, self._mv_th_v])
                self.appendRow([_t_limit_k, self._t_limit_v])
                self.appendRow(self._v_lim)
                self.appendRow([_pwm_lim_k, self._pwm_lim_v])
                self.appendRow([_curr_lim_k, self._curr_lim_v])
                self.appendRow([_vel_lim, self._vel_lim_v])
                self.appendRow(self._pos_lim)
                self.appendRow(self._v_pid)
                self.appendRow(self._p_pid)
                self.appendRow([_ff1, self._ff1_v])
                self.appendRow([_ff2, self._ff2_v])
                self.appendRow([_map_k, self._map_v])
                self.appendRow([_dir_k, self._dir_v])

            @pyqtSlot()
            def UpdateTree(self, data:SenConfigModel):
                self._port_v.setText(data.port)
                self._id_v.setText(str(data.id))
                self._baud_v.setText(str(data.baud_rate))
                self._d_mode_v.setText(str(data.drive_mode))
                self._op_mode_v.setText(str(data.op_mode))
                self._mv_th_v.setText(str(data.moving_threshold))
                self._t_limit_v.setText(str(data.temp_limit))
                self._v_lim.UpdateLimit(data.volt_limt)
                self._pwm_lim_v.setText(str(data.pwm_limit))
                self._curr_lim_v.setText(str(data.current_limt))
                self._vel_lim_v.setText(str(data.velocity_limit))
                self._pos_lim.UpdateLimit(data.position_limit)
                self._v_pid.UpdatePID(data.velocity_pid)
                self._p_pid.UpdatePID(data.position_pid)
                self._ff1_v.setText(str(data.FFGain1))
                self._ff2_v.setText(str(data.FFGain2))
                self._map_v.setText(str(data.mappings))
                self._dir_v.setText(str(data.direction))

        def __init__(self, parent=None):
            super().__init__(parent)

            _model = QStandardItemModel()
            _model.setHorizontalHeaderLabels(["Key", "Value"])

            _tree = QTreeView()
            _tree.setModel(_model)

            self._left_port_v = self.SenConfigItem("Left Config")
            self._right_port_v = self.SenConfigItem("Right Config")

            _model.appendRow(self._left_port_v)
            _model.appendRow(self._right_port_v)

            _central_v_box = QVBoxLayout()

            _central_v_box.addWidget(_tree)
            self.setLayout(_central_v_box)

        @pyqtSlot(SenConfigModel)
        def UpdateLeft(self, left: SenConfigModel):
            self._left_port_v.UpdateTree(left)

        @pyqtSlot(SenConfigModel)
        def UpdateRight(self, right: SenConfigModel):
            self._right_port_v.UpdateTree(right)


    def __init__(self, parent=None):
        super().__init__(parent)

        _m_client = MqttClient.get_instance()

        center_h_box = QHBoxLayout()
        
        sensor_v_box = QVBoxLayout()
        sensor_v_box.addWidget(QLabel("Sensor Data"))
        self._sensor_tree = DataViewWidget.SensorDataTree()
        sensor_v_box.addWidget(self._sensor_tree)

        sen_v_box = QVBoxLayout()
        sen_v_box.addWidget(QLabel("Sen Telemetry"))
        self._sen_tele_tree = DataViewWidget.SenTeleTree()
        sen_v_box.addWidget(self._sen_tele_tree)

        sen_conf_v_box = QVBoxLayout()
        sen_conf_v_box.addWidget(QLabel("Sen Config"))
        self._sen_config_tree = DataViewWidget.SenConfigTree()
        sen_conf_v_box.addWidget(self._sen_config_tree)

        center_h_box.addLayout(sensor_v_box)
        center_h_box.addLayout(sen_v_box)
        center_h_box.addLayout(sen_conf_v_box)
        self.setLayout(center_h_box)

        _m_client.DaqDataSignal.connect(self._sensor_tree.UpdateTree)
        _m_client.DaqConnectedSignal.connect(self._sensor_tree.UpdateCon)

        _m_client.SenTeleLeftSignal.connect(self._sen_tele_tree.UpdateLeft)
        _m_client.LeftSenConnectedSignal.connect(self._sen_tele_tree.LeftCon)

        _m_client.SenTeleRightSignal.connect(self._sen_tele_tree.UpdateRight)
        _m_client.RightSenConnectedSignal.connect(self._sen_tele_tree.RightCon)

        _m_client.SenLeftConfigSignal.connect(self._sen_config_tree.UpdateLeft)
        _m_client.SenRightConfigsignal.connect(self._sen_config_tree.UpdateRight)

