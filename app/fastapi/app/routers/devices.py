# app/routers/devices.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.database import get_db
from ..models.device import Device
from ..models.device_latest import DeviceLatest
from ..schemas.device import DeviceRead, DeviceWithLatest
from ..schemas.enums import DeviceStatus

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)


@router.get(
    "",
    summary="List devices",
    response_model=list[DeviceRead],
)
async def list_devices(
    account_id: int | None = Query(
        default=None,
        description="Optional filter: only devices for this account_id",
    ),
    status: DeviceStatus | None = Query(
        default=None,
        description="Optional filter: device status (active, suspended, etc.)",
    ),
    type: str | None = Query(
        default=None,
        description="Optional filter: device type (sensor, robot, tracker, ...)",
    ),
    name_search: str | None = Query(
        default=None,
        description="Optional substring search in device name (case-insensitive)",
    ),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of devices to return",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Offset for pagination",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[DeviceRead]:
    """
    Return a paginated list of devices.

    Read-only. Supports filters that align with your indexes:
    - account_id
    - status
    - type
    - simple name substring search
    """
    stmt = (
        select(Device)
        .order_by(Device.id)
        .offset(offset)
        .limit(limit)
    )

    if account_id is not None:
        stmt = stmt.where(Device.account_id == account_id)

    if status is not None:
        # status is a DeviceStatus enum, column is mapped to same enum
        stmt = stmt.where(Device.status == status)

    if type is not None:
        stmt = stmt.where(Device.type == type)

    if name_search is not None:
        # simple ILIKE search; not indexed but good enough for dev
        stmt = stmt.where(Device.name.ilike(f"%{name_search}%"))

    result = await db.execute(stmt)
    devices = result.scalars().all()

    return [DeviceRead.model_validate(d) for d in devices]


@router.get(
    "/{device_id}",
    summary="Get device by ID (optionally with latest location)",
    response_model=DeviceWithLatest,
)
async def get_device(
    device_id: int,
    include_latest: bool = Query(
        default=True,
        description="If true, include latest location from device_latest table",
    ),
    db: AsyncSession = Depends(get_db),
) -> DeviceWithLatest:
    """
    Get a single device by ID.

    By default, also includes the latest location (if present) from `device_latest`.
    """
    stmt = select(Device).where(Device.id == device_id)

    if include_latest:
        stmt = stmt.options(selectinload(Device.latest))

    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    # If include_latest=False, Device.latest may not be loaded,
    # but DeviceWithLatest.latest is allowed to be None.
    return DeviceWithLatest.model_validate(device)
