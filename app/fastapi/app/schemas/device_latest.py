# schemas/device_latest.py
from datetime import datetime

from .base import ORMModel


class DeviceLatestRead(ORMModel):
    device_id: int
    recorded_at: datetime
    x_coord: float
    y_coord: float
    meta: dict
