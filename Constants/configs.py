from pydantic import BaseModel
from typing import List


class MQTTConfig(BaseModel):
    host_name: str = "ncm.local"
    host_port: int = 1883


class LoggerConfig(BaseModel):
    log_name: str = "Log"
    mqtt_config: MQTTConfig


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
        ["pink", "c", "orange", "brown"],  # LQ, LL, RQ, RR
        ["r", "g"],  # left, right
    ]
    display_data_topic: str = "NCM/DisplayData"


class ExperimentMqttConfig:
    base_topic: str = "NCM/Experiment/"
    start_topic: str = "Start"
    stop_topic: str = "Stop"
    rename_topic: str = "Rename"
    elapsed_topic: str = "Elapsed"

class Sen1MqttConfig:
    base_topic: str = "NCM/SEN1/"
    # Pubs
    goal_position_topic: str = "goal/position"
    goal_mm_topic: str = "goal/mm"
    goal_index_topic: str = "goal/index"
    jog_topic: str = "jog"
    home_topic: str = "home"
    set_home_topic: str = "set_home"
    map_topic: str = "map"
    get_config_topic: str = "get_config"

    # Subs
    config_topic: str = "config"
    telemetery_json_topic: str = "telemetery/json"

class Sen2MqttConfig:
    base_topic: str = "NCM/SEN2"
    # Pubs
    goal_position_topic: str = "goal/position"
    goal_mm_topic: str = "goal/mm"
    goal_index_topic: str = "goal/index"
    jog_topic: str = "jog"
    home_topic: str = "home"
    set_home_topic: str = "set_home"
    map_topic: str = "map"
    get_config_topic: str = "get_config"

    # Subs
    config_topic: str = "config"
    telemetery_json_topic: str = "telemetery/json"
