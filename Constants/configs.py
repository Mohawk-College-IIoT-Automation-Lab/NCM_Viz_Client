from pydantic import BaseModel
from typing import List

class MQTTConfig(BaseModel):
    host_name: str = "localhost"
    host_port: int = 1883

class LoggerConfig(BaseModel):
    log_name: str = "Log"
    mqtt_config: MQTTConfig

class FilterConfig:
    type: str = "none"
    order: int = 0
    lpf_cutoff: float = 0
    hpf_cutoff: float = 0

class LowPassConfig(FilterConfig):
    type: str = "lowpass"
    order: int = 5
    lpf_cutoff: float = 500.0

class HighPassConfig(FilterConfig):
    type: str = "highpass"
    order: int = 5
    hpf_cutoff: float = 1.0

class BandPassConfig(FilterConfig):
    type: str = "bandpass"
    order: int = 5
    lpf_cutoff: float = 500.0
    hpf_cutoff: float = 0.5

class DAQConfig:
    device_name: str = "Dev2"
    physical_names: List[str] = ["ai0", "ai1", "ai2", "ai3", "ai4", "ai5", "ai6", "ai7"]
    channel_names: List[str] = ["USD-LL", "USD-LQ", "USD-RQ", "USD-RR", "ANM-LL", "ANM-LQ", "ANM-RQ", "ANM-RR"]
    usd_min: float = 0.0
    usd_max: float = 500.0
    anm_min: float = 0.0
    anm_max: float = 12.0
    v_min = 0
    v_max = 10
    file_name: str = "default.tdms"
    fs: int = 1000
    fs_disp: int = 10
    filter_config: FilterConfig = BandPassConfig()
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
        ['pink', 'c'],
        ['orange', 'brown'],
        ['r', 'g']
    ]
    display_data_topic: str = "NCM/DisplayData"

class ExperimentMqttConfig:
    base_topic:str = "NCM/Experiment/"
    start_topic:str = "Start"
    stop_topic:str = "Stop"
    rename_topic:str = "Rename"
    elapsed_topic:str = "Elapsed"

