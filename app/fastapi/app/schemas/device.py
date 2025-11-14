from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DeviceBase(BaseModel):
    name: str
    type: str


class DeviceRead(DeviceBase):
    """ 
    Schema: Query a device (Readonly)
    """
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
