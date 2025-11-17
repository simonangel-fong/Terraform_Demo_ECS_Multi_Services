# app/schemas/device.py
from datetime import datetime
from uuid import UUID
from pydantic import Field
from .base import ORMModel


class DeviceItem(ORMModel):
    name: str = Field(
        description="The device name",
    )
    device_uuid: UUID = Field(
        description="The UUID of the device",
    )
    tracking_enabled: bool = Field(
        description="Whether telemetry tracking is enabled for this device",
    )
    created_at: datetime
    updated_at: datetime
