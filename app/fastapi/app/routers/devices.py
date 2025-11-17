# app/routers/devices.py
from __future__ import annotations

import logging
from typing import List
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
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
from app.schemas.device import DeviceItem

# If you have an admin auth dependency, import and enable it here.
# from app.auth.dependencies import get_current_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    # Uncomment if this router should be admin-only:
    # dependencies=[Depends(get_current_admin_user)],
)


# ============================================================
# GET /devices
# ============================================================
@router.get(
    "",
    response_model=List[DeviceItem],
    summary="List registered devices",
    description=(
        "Return a paginated list of registered devices. "
        "Optionally filter results by tracking status.\n\n"
        "This endpoint is intended for administrative or operational use. "
        "IoT devices themselves should use the telemetry endpoints, not this API."
    ),
)
async def list_devices(
    tracking_enabled: bool | None = Query(
        default=None,
        description=(
            "If provided, returns only devices with the specified tracking status. "
            "`true` returns devices with tracking enabled, `false` returns devices "
            "with tracking explicitly disabled."
        ),
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description=(
            "Maximum number of devices to return. "
            "Use together with `offset` for pagination."
        ),
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description=(
            "Number of devices to skip before starting to collect the result set. "
            "Use together with `limit` for pagination."
        ),
    ),
    db: AsyncSession = Depends(get_db),
) -> list[DeviceItem]:
    """
    List registered devices with optional filtering and pagination.

    The result set is ordered by `created_at` in descending order so that newly
    registered devices appear first. This endpoint is typically used by
    administrative dashboards, monitoring services, or operational tooling.
    """
    logger.debug(
        "Listing devices",
        extra={
            "tracking_enabled": tracking_enabled,
            "limit": limit,
            "offset": offset,
        },
    )

    stmt = select(Device)

    if tracking_enabled is not None:
        stmt = stmt.where(Device.tracking_enabled == tracking_enabled)

    # Explicit ordering ensures deterministic pagination.
    stmt = stmt.order_by(Device.created_at.desc()).limit(limit).offset(offset)

    try:
        result = await db.execute(stmt)
        devices = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while listing devices",
            extra={
                "tracking_enabled": tracking_enabled,
                "limit": limit,
                "offset": offset,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve device list.",
        ) from exc

    logger.debug(
        "Successfully listed devices",
        extra={
            "tracking_enabled": tracking_enabled,
            "limit": limit,
            "offset": offset,
            "returned_count": len(devices),
        },
    )
    return devices


# ============================================================
# GET /devices/{device_uuid}
# ============================================================
@router.get(
    "/{device_uuid}",
    response_model=DeviceItem,
    summary="Get a device by UUID",
    description=(
        "Retrieve a single device using its globally unique device UUID. "
        "This UUID is typically the identifier burned into the device firmware.\n\n"
        "This endpoint is intended for administrative or operational use. "
        "IoT devices should authenticate using their UUID and API key via the "
        "telemetry APIs, rather than calling this endpoint directly."
    ),
)
async def get_device_by_uuid(
    device_uuid: UUID = Path(
        ...,
        description="Device UUID assigned by the system and burned into firmware.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
    db: AsyncSession = Depends(get_db),
) -> DeviceItem:
    """
    Retrieve a device by its UUID.

    This endpoint is typically used by admin tools or internal services
    to inspect or troubleshoot registered devices. It does not expose
    any secret material such as API keys or hashes; the response schema
    (`DeviceItem`) must be defined accordingly.
    """
    logger.debug(
        "Fetching device by UUID",
        extra={"device_uuid": str(device_uuid)},
    )

    stmt = select(Device).where(Device.device_uuid == device_uuid)

    try:
        result = await db.execute(stmt)
        device = result.scalar_one_or_none()
    except SQLAlchemyError as exc:
        logger.exception(
            "Database error while fetching device by UUID",
            extra={"device_uuid": str(device_uuid)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve device.",
        ) from exc

    if device is None:
        logger.info(
            "Device not found",
            extra={"device_uuid": str(device_uuid)},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    logger.debug(
        "Device fetched successfully",
        extra={"device_uuid": str(device_uuid)},
    )
    return device
