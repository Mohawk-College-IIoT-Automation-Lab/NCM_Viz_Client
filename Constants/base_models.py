from pydantic import BaseModel

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
    Standing_Wave: StandingWave
    Anemometer: SensorReadings