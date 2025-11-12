from datetime import datetime
from pydantic import BaseModel, Field


class TripBase(BaseModel):
    start_time: datetime | None = Field(
        default=None, description="TZ-aware timestamp")
    start_station: str


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    start_time: datetime | None = None
    start_station: str | None = None


class TripOut(TripBase):
    trip_id: int


class Config:
    from_attributes = True
