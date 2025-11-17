# app/schemas/device_telemetry.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .base import ORMModel


class TelemetryCreate(BaseModel):
    """
    Request body schema for creating a telemetry record from a device.

    Notes:
    - The device is identified by its UUID in the request path
      (e.g. POST /telemetry/{device_uuid}), not in this payload.
    - `recorded_at` is set server-side at ingestion time in UTC.
    - `device_time` is an optional timestamp reported by the device itself.
    """

    x_coord: float = Field(
        description="X coordinate value (double precision).",
        examples=[123.456],
    )
    y_coord: float = Field(
        description="Y coordinate value (double precision).",
        examples=[78.9],
    )
    device_time: Optional[datetime] = Field(
        default=None,
        description=(
            "Timestamp reported by the device clock (optional). "
            "If provided, it SHOULD be a timezone-aware datetime in UTC."
        ),
        examples=["2025-11-17T12:34:56Z"],
    )


class TelemetryItem(ORMModel):
    """
    A telemetry record returned to the device.

    Typical usage:
      - Response model for GET /telemetry/{device_uuid}
      - Response model for POST /telemetry/{device_uuid}

    The payload is intentionally minimal and does not expose internal
    database identifiers such as the telemetry row ID or the numeric
    device ID, because the device already identifies itself by UUID.
    """

    x_coord: float = Field(
        description="X coordinate value.",
        examples=[123.456],
    )
    y_coord: float = Field(
        description="Y coordinate value.",
        examples=[78.9],
    )
    recorded_at: datetime = Field(
        description=(
            "Server-side timestamp (UTC) when the telemetry record was stored. "
            "This is the authoritative time used for queries and partitioning."
        ),
        examples=["2025-11-17T12:35:00Z"],
    )
    device_time: Optional[datetime] = Field(
        default=None,
        description=(
            "Timestamp reported by the device (may differ from recorded_at due "
            "to network delay or clock skew)."
        ),
        examples=["2025-11-17T12:34:56Z"],
    )
