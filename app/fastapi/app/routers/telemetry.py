# app/routers/telemetry.py
from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Path,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.device import Device
from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryItem, TelemetryCreate

router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)

logger = logging.getLogger(__name__)

DEFAULT_LATEST_SECONDS = 1800       # 30 minutes
MAX_LATEST_SECONDS = 24 * 3600      # 24 hours


# ============================================================
# Helper functions
# ============================================================
def verify_api_key(api_key: str, stored_hash: str | None) -> bool:
    """
    Verify a plain-text API key against a stored SHA-256 hex digest.

    The stored hash is a 64-character hex string (from a CHAR(64) column)
    and may contain leading/trailing whitespace. This function performs
    a constant-time comparison to reduce timing side-channel risks.

    Parameters
    ----------
    api_key : str
        Plain-text API key presented by the device.
    stored_hash : str | None
        Hex-encoded SHA-256 digest stored in the database.

    Returns
    -------
    bool
        True if the API key matches the stored hash, False otherwise.
    """
    if not stored_hash:
        return False

    stored_hash = stored_hash.strip().lower()
    candidate_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    return hmac.compare_digest(candidate_hash, stored_hash)


def normalize_time_window(
    start_time: datetime | None,
    end_time: datetime | None,
    latest_seconds: int,
) -> tuple[datetime, datetime]:
    """
    Normalize the requested time window into a concrete [start_time, end_time] in UTC.

    Rules:
    - If either start_time or end_time is provided:
        * end_time missing  -> defaults to now() in UTC.
        * start_time missing -> defaults to end_time - MAX_LATEST_SECONDS (bounded lookback).
      In this case, `latest_seconds` is ignored.
    - If neither is provided:
        * Use [now() - latest_seconds, now()] in UTC.
    - All datetimes are converted to timezone-aware UTC.
    - If start_time is after end_time, an HTTP 400 is raised.

    Parameters
    ----------
    start_time : datetime | None
        Optional start of the time range.
    end_time : datetime | None
        Optional end of the time range.
    latest_seconds : int
        Lookback window in seconds when explicit times are not provided.

    Returns
    -------
    (datetime, datetime)
        Tuple of (start_time_utc, end_time_utc).
    """
    now_utc = datetime.now(timezone.utc)

    if start_time or end_time:
        # Normalize end_time first
        if end_time is None:
            end_time = now_utc
        elif end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        else:
            end_time = end_time.astimezone(timezone.utc)

        # Default start_time to a bounded range behind end_time
        if start_time is None:
            start_time = end_time - timedelta(seconds=MAX_LATEST_SECONDS)
        elif start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        else:
            start_time = start_time.astimezone(timezone.utc)
    else:
        end_time = now_utc
        start_time = end_time - timedelta(seconds=latest_seconds)

    if start_time > end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be before end_time.",
        )

    return start_time, end_time


async def get_authenticated_device(
    device_uuid: UUID = Path(
        ...,
        description="Device UUID burned into firmware and registered in the system.",
    ),
    api_key: str = Header(
        ...,
        alias="X-API-Key",
        description="Plain-text API key issued to this device.",
    ),
    db: AsyncSession = Depends(get_db),
) -> Device:
    """
    Authenticate a device using its UUID and API key.

    This dependency performs the following steps:
    1. Look up the device by UUID with `tracking_enabled = TRUE`.
    2. Verify the provided API key against the stored hash.
    3. Return the Device ORM instance on success.

    Raises
    ------
    HTTPException
        404 if the device is not found or tracking is disabled.
        401 if the API key is invalid.
    """
    logger.debug(
        "Authenticating device",
        extra={"device_uuid": str(device_uuid)},
    )

    stmt = (
        select(Device)
        .where(
            Device.device_uuid == device_uuid,
            Device.tracking_enabled.is_(True),
        )
    )

    try:
        result = await db.execute(stmt)
        device = result.scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while authenticating device",
            extra={"device_uuid": str(device_uuid)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate device.",
        ) from exc

    # For security, do not distinguish between "not found" and "tracking disabled".
    if device is None:
        logger.info(
            "Device not found or tracking disabled",
            extra={"device_uuid": str(device_uuid)},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or tracking disabled.",
        )

    if not verify_api_key(api_key=api_key, stored_hash=device.api_key_hash):
        logger.info(
            "Invalid API key for device",
            extra={"device_uuid": str(device_uuid)},
        )
        # 401 is appropriate for invalid credentials; 404 could be used to reduce key enumeration.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    logger.debug(
        "Device authenticated successfully",
        extra={"device_uuid": str(device_uuid)},
    )
    return device


# ============================================================
# GET /telemetry/{device_uuid}
# ============================================================
@router.get(
    "/{device_uuid}",
    summary="List telemetry for a device",
    description=(
        "Return a list of telemetry records for a specific device, identified by its UUID. "
        "The device must authenticate using the `X-API-Key` header. The time window can "
        "be specified using `start_time` and `end_time`, or by using `latest_seconds` "
        "to request data from a recent lookback period.\n\n"
        "Results are ordered by `recorded_at` in descending order (most recent first)."
    ),
    response_model=list[TelemetryItem],
)
async def list_telemetry_for_device(
    device: Device = Depends(get_authenticated_device),
    start_time: datetime | None = Query(
        default=None,
        description=(
            "Start of the time range (UTC). If provided, `latest_seconds` is ignored. "
            "If omitted while `end_time` is provided, the server will bound the lookback "
            f"window to at most {MAX_LATEST_SECONDS} seconds."
        ),
    ),
    end_time: datetime | None = Query(
        default=None,
        description=(
            "End of the time range (UTC). If omitted but `start_time` is provided, "
            "defaults to the current server time."
        ),
    ),
    latest_seconds: int = Query(
        default=DEFAULT_LATEST_SECONDS,
        ge=1,
        le=MAX_LATEST_SECONDS,
        description=(
            "Lookback window in seconds when `start_time` and `end_time` are not provided. "
            "The server returns telemetry in the range [now() - latest_seconds, now()]."
        ),
    ),
    limit: int = Query(
        default=1000,
        ge=1,
        le=5000,
        description="Maximum number of telemetry records to return.",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[TelemetryItem]:
    """
    Device-facing telemetry listing endpoint.

    This endpoint is intended to be called by the device itself or by a trusted
    client acting on behalf of the device. The device is authenticated via its
    UUID (path) and API key (header). Only telemetry for the authenticated device
    is returned.
    """
    start_time, end_time = normalize_time_window(
        start_time=start_time,
        end_time=end_time,
        latest_seconds=latest_seconds,
    )

    logger.debug(
        "Listing telemetry for device",
        extra={
            "device_id": device.id,
            "device_uuid": str(device.device_uuid),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "limit": limit,
        },
    )

    stmt = (
        select(Telemetry)
        .where(
            Telemetry.device_id == device.id,
            Telemetry.recorded_at >= start_time,
            Telemetry.recorded_at <= end_time,
        )
        .order_by(Telemetry.recorded_at.desc())
        .limit(limit)
    )

    try:
        result = await db.execute(stmt)
        rows = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while listing telemetry",
            extra={
                "device_id": device.id,
                "device_uuid": str(device.device_uuid),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve telemetry.",
        ) from exc

    logger.debug(
        "Telemetry listing succeeded",
        extra={
            "device_id": device.id,
            "device_uuid": str(device.device_uuid),
            "returned_count": len(rows),
        },
    )
    return rows


# ============================================================
# POST /telemetry/{device_uuid}
# ============================================================
@router.post(
    "/{device_uuid}",
    summary="Ingest telemetry for a device",
    description=(
        "Ingest a single telemetry record for a specific device identified by its UUID. "
        "The device must authenticate using the `X-API-Key` header. The server assigns "
        "`recorded_at` based on the current time in UTC. The device may optionally include "
        "`device_time` to represent its own clock value."
    ),
    response_model=TelemetryItem,
    status_code=status.HTTP_201_CREATED,
)
async def create_telemetry_for_device(
    device: Device = Depends(get_authenticated_device),
    payload: TelemetryCreate = Body(
        ...,
        description="Telemetry payload containing coordinates and optional device timestamp.",
    ),
    db: AsyncSession = Depends(get_db),
) -> TelemetryItem:
    """
    Ingest a single telemetry record for the authenticated device.

    The device is authenticated via `get_authenticated_device`. The server
    sets `recorded_at` to the current UTC time. On success, the stored
    telemetry record is returned.
    """
    now_utc = datetime.now(timezone.utc)

    telemetry = Telemetry(
        device_id=device.id,
        x_coord=payload.x_coord,
        y_coord=payload.y_coord,
        recorded_at=now_utc,
        device_time=payload.device_time,
    )

    db.add(telemetry)

    try:
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception(
            "Database error while storing telemetry",
            extra={
                "device_id": device.id,
                "device_uuid": str(device.device_uuid),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store telemetry.",
        ) from exc

    logger.debug(
        "Telemetry stored successfully",
        extra={
            "device_id": device.id,
            "device_uuid": str(device.device_uuid),
            "recorded_at": telemetry.recorded_at.isoformat(),
        },
    )
    return telemetry
