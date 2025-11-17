# app/routers/telemetry.py
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ..db.database import get_db
from ..models.device import Device
from ..models.device_telemetry import DeviceTelemetry
from ..models.device_latest import DeviceLatest
from ..schemas.device_telemetry import (
    TelemetryRead,
    TelemetryCreate,
    TelemetryBatchCreate,
)

router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)

DEFAULT_LATEST_SECONDS = 1800         # 30 minutes
MAX_LATEST_SECONDS = 24 * 3600        # safety: 24 hours


# ============================================================
# READ: list telemetry
# ============================================================
@router.get(
    "",
    summary="List telemetry (optionally by device, latest N seconds)",
    response_model=list[TelemetryRead],
)
async def list_telemetry(
    device_id: int | None = Query(
        default=None,
        description="Optional filter: only telemetry for this device_id",
    ),
    latest: int = Query(
        DEFAULT_LATEST_SECONDS,
        ge=1,
        le=MAX_LATEST_SECONDS,
        description=(
            "Time window in seconds (e.g. 1800 = last 30 minutes). "
            "Defaults to 1800. Max 86400 (24 hours)."
        ),
    ),
    limit: int = Query(
        1000,
        ge=1,
        le=10000,
        description="Maximum number of telemetry rows to return",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[TelemetryRead]:
    cutoff_expr = func.now() - timedelta(seconds=latest)

    stmt = (
        select(DeviceTelemetry)
        .where(DeviceTelemetry.recorded_at >= cutoff_expr)
        .order_by(DeviceTelemetry.recorded_at.desc())
        .limit(limit)
    )

    if device_id is not None:
        stmt = stmt.where(DeviceTelemetry.device_id == device_id)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    return [TelemetryRead.model_validate(r) for r in rows]


@router.get(
    "/{device_id}",
    summary="List telemetry for a specific device (latest N seconds)",
    response_model=list[TelemetryRead],
)
async def list_device_telemetry(
    device_id: int,
    latest: int = Query(
        DEFAULT_LATEST_SECONDS,
        ge=1,
        le=MAX_LATEST_SECONDS,
        description=(
            "Time window in seconds for this device. "
            "Defaults to 1800 (30 minutes). Max 86400 (24 hours)."
        ),
    ),
    limit: int = Query(
        1000,
        ge=1,
        le=10000,
        description="Maximum number of telemetry rows to return",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[TelemetryRead]:
    cutoff_expr = func.now() - timedelta(seconds=latest)

    stmt = (
        select(DeviceTelemetry)
        .where(DeviceTelemetry.device_id == device_id)
        .where(DeviceTelemetry.recorded_at >= cutoff_expr)
        .order_by(DeviceTelemetry.recorded_at.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.scalars().all()

    return [TelemetryRead.model_validate(r) for r in rows]


# ============================================================
# WRITE: single telemetry point
# ============================================================
@router.post(
    "",
    summary="Ingest a single telemetry point",
    response_model=TelemetryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_telemetry(
    payload: TelemetryCreate,
    db: AsyncSession = Depends(get_db),
) -> TelemetryRead:
    """
    Insert a single telemetry row and update:
    - device_telemetry
    - device_latest (upsert)
    - device.last_seen_at
    """
    # Optional: ensure device exists
    device = await db.get(Device, payload.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    recorded_at = payload.recorded_at or datetime.now(timezone.utc)

    telemetry = DeviceTelemetry(
        device_id=payload.device_id,
        recorded_at=recorded_at,
        x_coord=payload.x_coord,
        y_coord=payload.y_coord,
        meta=payload.meta,
    )
    db.add(telemetry)

    # Upsert into device_latest:
    #   - Insert new row if none exists
    #   - Update only if this telemetry is newer than existing recorded_at
    stmt_latest = pg_insert(DeviceLatest).values(
        device_id=payload.device_id,
        recorded_at=recorded_at,
        x_coord=payload.x_coord,
        y_coord=payload.y_coord,
        meta=payload.meta or {},
    ).on_conflict_do_update(
        index_elements=[DeviceLatest.device_id],
        set_={
            "recorded_at": recorded_at,
            "x_coord": payload.x_coord,
            "y_coord": payload.y_coord,
            "meta": payload.meta or {},
        },
        where=DeviceLatest.recorded_at < recorded_at,
    )
    await db.execute(stmt_latest)

    # Update device.last_seen_at
    await db.execute(
        update(Device)
        .where(Device.id == payload.device_id)
        .values(last_seen_at=recorded_at)
    )

    await db.commit()
    await db.refresh(telemetry)

    return TelemetryRead.model_validate(telemetry)


# ============================================================
# WRITE: batch telemetry for a single device
# ============================================================
@router.post(
    "/batch",
    summary="Ingest multiple telemetry points for a single device",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def create_telemetry_batch(
    payload: TelemetryBatchCreate,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Efficient batch insert for a single device.

    - Inserts multiple rows into device_telemetry
    - Updates device_latest using the newest recorded_at in the batch
    - Updates device.last_seen_at
    """
    # Ensure device exists
    device = await db.get(Device, payload.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    now_utc = datetime.now(timezone.utc)
    telemetry_rows: list[DeviceTelemetry] = []
    latest_ts: datetime | None = None
    latest_point: TelemetryCreate | None = None

    for p in payload.points:
        recorded_at = p.recorded_at or now_utc

        row = DeviceTelemetry(
            device_id=payload.device_id,
            recorded_at=recorded_at,
            x_coord=p.x_coord,
            y_coord=p.y_coord,
            meta=p.meta,
        )
        telemetry_rows.append(row)

        if latest_ts is None or recorded_at > latest_ts:
            latest_ts = recorded_at
            latest_point = p

    if not telemetry_rows:
        # No points submitted; nothing to do
        return

    db.add_all(telemetry_rows)

    # Upsert latest only once (for the newest point)
    if latest_ts is not None and latest_point is not None:
        stmt_latest = pg_insert(DeviceLatest).values(
            device_id=payload.device_id,
            recorded_at=latest_ts,
            x_coord=latest_point.x_coord,
            y_coord=latest_point.y_coord,
            meta=latest_point.meta or {},
        ).on_conflict_do_update(
            index_elements=[DeviceLatest.device_id],
            set_={
                "recorded_at": latest_ts,
                "x_coord": latest_point.x_coord,
                "y_coord": latest_point.y_coord,
                "meta": latest_point.meta or {},
            },
            where=DeviceLatest.recorded_at < latest_ts,
        )
        await db.execute(stmt_latest)

        # Update device.last_seen_at
        await db.execute(
            update(Device)
            .where(Device.id == payload.device_id)
            .values(last_seen_at=latest_ts)
        )

    await db.commit()
    # 204: no body
