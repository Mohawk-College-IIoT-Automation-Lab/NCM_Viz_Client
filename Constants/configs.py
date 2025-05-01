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
    channels: List[str] = ["Dev2/ai0", "Dev2/ai1", "Dev2/ai2", "Dev2/ai3"]
    channel_names: List[str] = ["USD1", "USD2", "USD3", "USD4"]
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
    display_data_topic: str = "NCM/DisplayData"

class ExperimentMqttConfig:
    base_topic:str = "NCM/Experiment/"
    start_topic:str = "Start"
    stop_topic:str = "Stop"
    rename_topic:str = "Rename"
    elapsed_topic:str = "Elapsed"

