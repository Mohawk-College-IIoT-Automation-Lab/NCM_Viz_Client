from enum import Enum 
from typing import List
from pydantic import BaseModel

class SenPorts(Enum):
    LeftPort = "LEFT"
    RightPort = "RIGHT"

class Limits(BaseModel):
    min: int
    max: int

class PID(BaseModel):
    P: int 
    I: int 
    D: int

class Mapping(BaseModel):
    mm: float 
    position: int


class SenConfigModel(BaseModel):
    port: str
    id: int
    baud_rate: int
    drive_mode: int
    op_mode: int
    moving_threshold: int
    temp_limit: int
    volt_limt: Limits
    pwm_limit: int
    current_limt: int
    velocity_limit: int
    position_limit: Limits 
    velocity_pid: PID 
    position_pid: PID
    FFGain1: int
    FFGain2: int
    mappings: List[Mapping]
    direction: bool

class BaseTelemetry(BaseModel):
    pwm: int 
    current: int 
    velocity: int 
    position: int
    percent: int

class SenTelemetry(BaseModel):
    goal_telemetry: BaseTelemetry
    moving: int 
    moving_status: int 
    present_telmetry: BaseTelemetry
    velocity_trajectory: int
    position_trajectory: int
    present_input_voltage: int
    present_temp: int

class SensorReadings(BaseModel):
    LL: float
    LQ: float
    RR: float
    RQ: float

class StandingWave(BaseModel):
    Left: float
    Right: float

class SensorData(BaseModel):
    Ultra_Sonic_Distance: SensorReadings
    Anemometer: SensorReadings
    Standing_Wave: StandingWave
