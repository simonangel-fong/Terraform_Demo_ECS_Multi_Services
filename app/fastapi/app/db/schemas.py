# schemas.py
from datetime import datetime
from pydantic import BaseModel, Field


# ---- Devices ----
class DeviceBase(BaseModel):
    name: str
    type: str


class DeviceCreate(DeviceBase):
    pass


class DeviceGet(DeviceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 ORM mode


# ---- Positions ----

class DevicePositionGet(BaseModel):
    device_id: int
    ts: datetime
    x: float
    y: float

    class Config:
        from_attributes = True


class DevicePositionUpdate(BaseModel):
    """Incoming payload to update/append a device position."""
    x: float = Field(
        ...,
        ge=0,
        le=10,
        description="X coordinate in range [0, 10]",
    )
    y: float = Field(
        ...,
        ge=0,
        le=10,
        description="Y coordinate in range [0, 10]",
    )
