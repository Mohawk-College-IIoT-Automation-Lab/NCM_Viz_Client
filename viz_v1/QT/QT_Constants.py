from pydantic import BaseModel
from typing import List

class SensorQTConfig:
    usd_left_title: str = "USD - Left Mould (LL, LQ)"
    usd_right_title: str = "USD - Right Mould (RQ, RR)"
    standing_wave_title: str = "Stating Wave Height (LL-LQ) (RR-RQ)"
    anm_left_title: str = "ANM - Left Mould (LL, LQ)"
    anm_right_title: str = "ANM - Right Mould (RQ, RR)"
    colors: List[List[str]] = [
        ["pink", "c", "orange", "brown"],  # LQ, LL, RQ, RR
        ["r", "g"],  # left, right
    ]

