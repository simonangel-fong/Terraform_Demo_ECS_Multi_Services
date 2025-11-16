# # schemas/device_telemetry.py
# from datetime import datetime

# from pydantic import BaseModel, Field

# from .base import ORMModel


# class TelemetryBase(BaseModel):
#     x_coord: float = Field(..., description="X coordinate")
#     y_coord: float = Field(..., description="Y coordinate")
#     recorded_at: datetime | None = Field(
#         default=None,
#         description="Optional timestamp; server will default to now() if omitted",
#     )
#     meta: dict | None = Field(
#         default=None,
#         description="Optional metadata JSON (battery, temp, etc.)",
#     )


# class TelemetryCreate(TelemetryBase):
#     device_id: int = Field(description="Target device ID")


# class TelemetryBatchCreate(BaseModel):
#     """insert multiple telemetry points in one request."""
#     device_id: int
#     points: list[TelemetryBase]


# class TelemetryRead(ORMModel):
#     id: int
#     device_id: int
#     recorded_at: datetime
#     x_coord: float
#     y_coord: float
#     meta: dict | None
