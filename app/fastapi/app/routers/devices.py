# app/routers/devices.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.device import Device
from app.schemas.device import DeviceItem

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)


@router.get("", response_model=list[DeviceItem])
async def list_devices(
    tracking_enabled: bool | None = Query(
        default=None,
        description="Filter by tracking_enabled if provided",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[DeviceItem]:
    stmt = select(Device)
    if tracking_enabled is not None:
        stmt = stmt.where(Device.tracking_enabled == tracking_enabled)

    result = await db.execute(stmt)
    devices = result.scalars().all()
    return devices


@router.get("/{device_id}", response_model=DeviceItem)
async def get_device_by_id(
    device_id: int,
    db: AsyncSession = Depends(get_db),
) -> DeviceItem:
    stmt = select(Device).where(Device.id == device_id)
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return device
