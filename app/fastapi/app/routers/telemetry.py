# app/routers/telemetry.py
from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Path, Query, status

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..models.device_registry import DeviceRegistry
from ..models.telemetry_event import TelemetryEvent
from ..schemas.telemetry_event import TelemetryCreate, TelemetryItem

from ..models.telemetry_latest import TelemetryLatest
from ..schemas.telemetry_latest import TelemetryLatestItem

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

    Notes:
    - The stored hash is expected to be a hex-encoded SHA-256 digest.
    - Comparison is done using hmac.compare_digest to reduce timing attacks.
    """
    if not stored_hash:
        return False
    stored_hash = stored_hash.strip().lower()
    candidate_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    print(candidate_hash)
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
        * start_time missing -> defaults to end_time - MAX_LATEST_SECONDS.
      In this case, latest_seconds is ignored.
    - If neither is provided:
        * Use [now() - latest_seconds, now()] in UTC.
    - All datetimes are converted to timezone-aware UTC.
    - If start_time is after end_time, an HTTP 400 is raised.
    """
    now_utc = datetime.now(timezone.utc)

    if start_time or end_time:
        # Normalize end_time
        if end_time is None:
            end_time = now_utc
        elif end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        else:
            end_time = end_time.astimezone(timezone.utc)

        # Normalize start_time with bounded lookback
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
        description="Device UUID burned into firmware and registered in the telemetry registry.",
    ),
    api_key: str = Header(
        ...,
        alias="X-API-Key",
        description="Plain-text API key issued to this device.",
    ),
    db: AsyncSession = Depends(get_db),
) -> DeviceRegistry:
    """
    Authenticate a device using its UUID and API key.

    Steps:
    1. Look up the device by device_uuid in DeviceRegistry.
    2. Verify the provided API key against the stored hash.
    3. Return the DeviceRegistry ORM instance on success.

    Errors:
    - 404 if the device is not found in the registry.
    - 401 if the API key is invalid.
    """
    logger.debug(
        "Authenticating device",
        extra={"device_uuid": str(device_uuid)},
    )

    stmt = select(DeviceRegistry).where(
        DeviceRegistry.device_uuid == device_uuid)

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

    if device is None:
        # Do not leak details about registry state beyond "not found".
        logger.info(
            "Device not found in registry",
            extra={"device_uuid": str(device_uuid)},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    if not verify_api_key(api_key=api_key, stored_hash=device.api_key_hash):
        logger.info(
            "Invalid API key for device",
            extra={"device_uuid": str(device_uuid)},
        )
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
        "Return a list of telemetry events for a specific device, identified by its UUID. "
        "The device must authenticate using the `X-API-Key` header. The time window can "
        "be specified using `start_time` and `end_time`, or by using `latest_seconds` "
        "to request data from a recent lookback period.\n\n"
        "Results are ordered by `system_time_utc` in descending order (most recent first)."
    ),
    response_model=list[TelemetryItem],
)
async def list_telemetry_for_device(
    device: DeviceRegistry = Depends(get_authenticated_device),
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
        default=100,
        ge=1,
        le=5000,
        description="Maximum number of telemetry records to return.",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[TelemetryItem]:
    """
    Device-facing telemetry listing endpoint.

    The device is authenticated via its UUID (path) and API key (header).
    Only telemetry for the authenticated device is returned.
    """
    start_time, end_time = normalize_time_window(
        start_time=start_time,
        end_time=end_time,
        latest_seconds=latest_seconds,
    )

    logger.debug(
        "Listing telemetry for device",
        extra={
            "device_uuid": str(device.device_uuid),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "limit": limit,
        },
    )

    stmt = (
        select(TelemetryEvent)
        .where(
            TelemetryEvent.device_uuid == device.device_uuid,
            TelemetryEvent.system_time_utc >= start_time,
            TelemetryEvent.system_time_utc <= end_time,
        )
        .order_by(TelemetryEvent.system_time_utc.desc())
        .limit(limit)
    )

    try:
        result = await db.execute(stmt)
        rows = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while listing telemetry",
            extra={
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
        "Ingest a single telemetry event for a specific device identified by its UUID. "
        "The device must authenticate using the `X-API-Key` header. The server assigns "
        "`system_time_utc` based on the current time in UTC. The device may optionally "
        "include `device_time` to represent its own clock value; if omitted, it will "
        "be set to the server ingestion time."
    ),
    response_model=TelemetryItem,
    status_code=status.HTTP_201_CREATED,
)
async def create_telemetry_for_device(
    device: DeviceRegistry = Depends(get_authenticated_device),
    payload: TelemetryCreate = Body(
        description="Telemetry payload containing coordinates and optional device timestamp.",
    ),
    db: AsyncSession = Depends(get_db),
) -> TelemetryItem:
    """
    Ingest a single telemetry event for the authenticated device.

    The device is authenticated via `get_authenticated_device`. The server
    sets `system_time_utc` to the current UTC time. If `device_time` is not
    provided in the payload, it is set to the same value as `system_time_utc`.
    """
    now_utc = datetime.now(timezone.utc)
    device_time = payload.device_time or now_utc

    telemetry = TelemetryEvent(
        device_uuid=device.device_uuid,
        x_coord=payload.x_coord,
        y_coord=payload.y_coord,
        device_time=device_time,
        system_time_utc=now_utc,
    )

    db.add(telemetry)

    try:
        await db.commit()
        await db.refresh(telemetry)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception(
            "Database error while storing telemetry",
            extra={"device_uuid": str(device.device_uuid)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store telemetry.",
        ) from exc

    logger.debug(
        "Telemetry stored successfully",
        extra={
            "device_uuid": str(device.device_uuid),
            "system_time_utc": telemetry.system_time_utc.isoformat(),
        },
    )
    return telemetry

# ============================================================
# GET /telemetry/latest/{device_uuid}
# ============================================================
@router.get(
    "/latest/{device_uuid}",
    summary="Get latest telemetry snapshot for a device",
    description=(
        "Return the latest known position for a specific device, identified by its UUID. "
        "The device must authenticate using the `X-API-Key` header.\n\n"
        "This endpoint reads from the telemetry_latest snapshot table, which is maintained "
        "by the backend whenever new telemetry events are ingested."
    ),
    response_model=TelemetryLatestItem,
)
async def get_latest_telemetry_for_device(
    device: DeviceRegistry = Depends(get_authenticated_device),
    db: AsyncSession = Depends(get_db),
) -> TelemetryLatestItem:
    """
    Return the latest telemetry snapshot for the authenticated device.

    If no telemetry has ever been ingested for this device, a 404 is returned.
    """
    logger.debug(
        "Fetching latest telemetry snapshot for device",
        extra={"device_uuid": str(device.device_uuid)},
    )

    stmt = select(TelemetryLatest).where(
        TelemetryLatest.device_uuid == device.device_uuid
    )

    try:
        result = await db.execute(stmt)
        latest = result.scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while fetching latest telemetry",
            extra={"device_uuid": str(device.device_uuid)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve latest telemetry.",
        ) from exc

    if latest is None:
        logger.info(
            "No telemetry snapshot found for device",
            extra={"device_uuid": str(device.device_uuid)},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No telemetry available for this device.",
        )

    logger.debug(
        "Latest telemetry snapshot fetched successfully",
        extra={
            "device_uuid": str(device.device_uuid),
            "system_time_utc": latest.system_time_utc.isoformat(),
        },
    )
    return latest
