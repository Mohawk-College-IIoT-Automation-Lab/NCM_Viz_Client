from pydantic import BaseModel
from typing import List

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

class BaseTelemetery(BaseModel):
    pwm : int 
    current : int 
    velocity : int
    position : int 

class XM430Telemetery(BaseModel):
    goal_telemetery : BaseTelemetery
    moving : int
    moving_status : int 
    present_telemetery : BaseTelemetery
    velocity_trajectory : int 
    position_trajectory : int 
    present_input_voltage : int 
    present_temp : int

class BaudConfig(BaseModel):
    baud : int 
    id : int

class LimitConfig(BaseModel):
    max : int 
    min : int 

class PIDConfig(BaseModel):
    D : int 
    I : int
    P : int 

class MappingConfig(BaseModel):
    mm : float
    position : int

class XM430Config(BaseModel):
    FFGain1 : int
    FFGain2 : int 
    baud_rate : BaudConfig
    current_limit : int 
    direction : bool 
    drive_mode : int 
    id : int 
    mapping : List[MappingConfig]
    moving_threshold : int
    op_mode : int 
    port : str
    position_limit : LimitConfig
    position_pid : PIDConfig
    pwm_limit : int 
    temp_limit : int 
    torque_limit : int 
    velocity_limit : int 
    velocity_pid : PIDConfig
    volt_limit : LimitConfig

