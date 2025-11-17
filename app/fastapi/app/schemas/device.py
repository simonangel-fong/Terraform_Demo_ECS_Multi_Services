# schemas/device.py
from datetime import datetime

from .base import ORMModel
from .enums import DeviceStatus
from .device_latest import DeviceLatestRead


class DeviceRead(ORMModel):
    id: int
    account_id: int
    name: str
    type: str
    model: str | None
    status: DeviceStatus
    firmware_version: str | None
    tags: dict | None
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DeviceWithLatest(DeviceRead):
    latest: DeviceLatestRead | None
