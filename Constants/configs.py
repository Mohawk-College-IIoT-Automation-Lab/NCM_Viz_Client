from pydantic import BaseModel
from typing import List

class MQTTConfig(BaseModel):
    host_name: str = "localhost"
    host_port: int = 1883

class LoggerConfig(BaseModel):
    log_name: str = "Log"
    mqtt_config: MQTTConfig

class DAQConfig:
    device_name: str = "cDAQ9185-2304EC6Mod3"
    physical_names: List[str] = ["ai0", "ai1", "ai2", "ai3", "ai4", "ai5", "ai6", "ai7"]
    channel_names: List[str] = ["USD-LL", "USD-LQ", "USD-RQ", "USD-RR", "ANM-LL", "ANM-LQ", "ANM-RQ", "ANM-RR"]
    usd_pre_min: float = 0
    usd_pre_max: float = 10
    usd_min: float = 100
    usd_max: float = 780
    anm_pre_min: float = 0
    anm_pre_max: float = 1
    anm_min: float = 0.04
    anm_max: float = 5.0
    offsets: list[float] = [
            3.0, # USD-RR
            0.0, # USD-RQ
            0.0, # USD-LQ
            6.0, # USD-LL
            0.0, # ANM-RR
            0.0, # ANM-RQ
            0.0, # ANM-LQ
            0.0, # ANM-LL
    ]
    usd_sig_figs: int = 0 
    anm_sig_figs: int = 2
    file_name: str = "default.tdms"
    lpf_order: int = 2
    fs: int = 2000
    fs_disp: int = 10
    lpf_cutoff: int = 500
    mqtt_config: MQTTConfig
    log_config: LoggerConfig

class StatusLightsConfig:
    alarm_names: List[str] = ["Alarm1", "Alarm2", "Alarm3", "Alarm4"]
    alarm_base_topic: str = "NCM/Alarms/"
    alarm_topics: List[str] = ["Alarm1", "Alarm2", "Alarm3", "Alarm4"]

class SensorsConfig:
    usd_left_title: str = "USD - Left Mould (LL, LQ)"
    usd_right_title: str = "USD - Right Mould (RQ, RR)"
    standing_wave_title: str = "Stating Wave Height (LL-LQ) (RR-RQ)"
    anm_left_title: str = "ANM - Left Mould (LL, LQ)"
    anm_right_title: str = "ANM - Right Mould (RQ, RR)"
    colors: List[List[str]] = [
        ['c', 'pink'], # LQ, LL
        ['orange', 'brown'], # RQ, RR
        ['r', 'g'] # left, right
    ]
    display_data_topic: str = "NCM/DisplayData"

class ExperimentMqttConfig:
    base_topic:str = "NCM/Experiment/"
    start_topic:str = "Start"
    stop_topic:str = "Stop"
    rename_topic:str = "Rename"
    elapsed_topic:str = "Elapsed"

