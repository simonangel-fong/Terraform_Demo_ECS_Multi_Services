from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DeviceBase(BaseModel):
    name: str
    type: str


class DeviceCreate(DeviceBase):
    """Schema: creating a new device"""
    pass


class DeviceRead(DeviceBase):
    """Schema: reading a device"""
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
