import logging
from typing import List, Annotated
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, status, Query, Path, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from .config.setting import settings
from .db.database import get_db
from .db.models import Device, DevicePosition
from .db.schemas import DeviceGet, DevicePositionGet, DevicePositionUpdate

# Basic logging config
logging.basicConfig(
    level=logging.INFO,  # change to DEBUG during development
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Device Tracking API")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/")
async def home():
    """
    Home endpoint.

    URL:
        GET /
    """
    return {
        "env": settings.env,
        "debug": settings.debug,
        "message": "Device tracking API is running. Use this service to query devices and their positions.",
    }


@app.get("/devices", response_model=List[DeviceGet])
async def list_devices(
    limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Max number of devices to return",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of devices to skip",
    ),
    db: AsyncSession = Depends(get_db),
) -> List[DeviceGet]:
    """
    Return a paginated list of registered devices ordered by ID.
    """
    logger.debug("Listing devices", extra={"limit": limit, "offset": offset})

    try:
        stmt = (
            select(Device)
            .order_by(Device.id)
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        devices = result.scalars().all()

        logger.info(
            "Devices fetched successfully",
            extra={"count": len(devices), "limit": limit, "offset": offset},
        )

        return devices

    except SQLAlchemyError:
        logger.exception("Failed to list devices from database")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get("/devices/info", response_model=DeviceGet)
async def get_device_by_name_and_type(
    name: str = Query(
        ...,
        min_length=1,
        max_length=255,
        description="Device name",
    ),
    device_type: str = Query(
        ...,
        min_length=1,
        max_length=100,
        alias="type",  # frontend still uses ?type=sensor
        description="Device type",
    ),
    db: AsyncSession = Depends(get_db),
) -> DeviceGet:
    """
    Get a single device by its name and type.

    Example:
        GET /devices/info?name=device-001&type=sensor
    """
    logger.debug(
        "Fetching device by name and type",
        extra={"name": name, "type": device_type},
    )

    stmt = select(Device).where(
        Device.name == name,
        Device.type == device_type,
    )
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if device is None:
        logger.info(
            "Device not found with given name and type",
            extra={"name": name, "type": device_type},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found with the given name and type",
        )

    logger.debug(
        "Device found",
        extra={"id": device.id, "name": device.name, "type": device.type},
    )
    return device


@app.get(
    "/device/position/last/{device_id}",
    response_model=DevicePositionGet,
    summary="Get latest position of a device by ID",
)
async def get_latest_position(
    device_id: Annotated[
        int,
        Path(
            ge=1,
            description="ID of the device",
        ),
    ],
    db: AsyncSession = Depends(get_db),
) -> DevicePositionGet:
    """
    Get the latest position of a device by its ID.

    Example:
        GET /device/position/last/1
    """
    logger.debug("Fetching latest position", extra={"device_id": device_id})

    # Check device exists
    stmt_device = select(Device).where(Device.id == device_id)
    res_device = await db.execute(stmt_device)
    device = res_device.scalar_one_or_none()
    if device is None:
        logger.info("Device not found", extra={"device_id": device_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    # Get most recent position
    stmt_pos = (
        select(DevicePosition)
        .where(DevicePosition.device_id == device_id)
        .order_by(DevicePosition.ts.desc())
        .limit(1)
    )
    res_pos = await db.execute(stmt_pos)
    latest = res_pos.scalar_one_or_none()

    if latest is None:
        logger.info(
            "No position data for device",
            extra={"device_id": device_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No position data for this device",
        )

    logger.debug(
        "Latest position fetched",
        extra={
            "device_id": latest.device_id,
            "ts": latest.ts.isoformat() if latest.ts else None,
        },
    )
    return latest


@app.get(
    "/device/position/track/{device_id}",
    response_model=List[DevicePositionGet],
    summary="Track recent movement of a device",
)
async def track_recent_movement(
    device_id: Annotated[
        int,
        Path(
            ge=1,
            description="ID of the device",
        ),
    ],
    seconds: int = Query(
        10,
        alias="sec",
        ge=1,
        le=600,
        description="Time window in seconds (default 10)",
    ),
    db: AsyncSession = Depends(get_db),
) -> List[DevicePositionGet]:
    """
    Track recent positions of a device over the last `seconds` (default 10).

    Examples:
        - GET /device/position/track/1
        - GET /device/position/track/1?sec=3
    """
    logger.debug(
        "Tracking recent movement",
        extra={"device_id": device_id, "seconds": seconds},
    )

    # Ensure device exists
    stmt_device = select(Device).where(Device.id == device_id)
    res_device = await db.execute(stmt_device)
    device = res_device.scalar_one_or_none()
    if device is None:
        logger.info("Device not found", extra={"device_id": device_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    now = datetime.now(timezone.utc)
    threshold = now - timedelta(seconds=seconds)

    stmt = (
        select(DevicePosition)
        .where(
            DevicePosition.device_id == device_id,
            DevicePosition.ts >= threshold,
        )
        .order_by(DevicePosition.ts.asc())
    )

    res = await db.execute(stmt)
    positions = res.scalars().all()

    logger.debug(
        "Movement query completed",
        extra={"device_id": device_id, "count": len(positions)},
    )

    return positions


@app.post(
    "/device/position/{device_id}",
    response_model=DevicePositionGet,
    status_code=status.HTTP_201_CREATED,
    summary="Append latest position for a device",
)
async def update_device_position(
    device_id: Annotated[
        int,
        Path(
            ge=1,
            description="ID of the device whose position is being updated",
        ),
    ],
    payload: DevicePositionUpdate,
    db: AsyncSession = Depends(get_db),
) -> DevicePositionGet:
    """
    Append a new position for the given device with `device_id` and the new `(x, y)`.

    Example:

        POST /device/position/3
        {
            "x": 4.5,
            "y": 7.2
        }
    """
    logger.debug(
        "Updating device position",
        extra={"device_id": device_id, "x": payload.x, "y": payload.y},
    )

    # Ensure device exists
    stmt_device = select(Device).where(Device.id == device_id)
    res_device = await db.execute(stmt_device)
    device = res_device.scalar_one_or_none()
    if device is None:
        logger.info(
            "Device not found when updating position",
            extra={"device_id": device_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    # Create a new position
    position = DevicePosition(
        device_id=device_id,
        x=payload.x,
        y=payload.y,
    )

    db.add(position)

    try:
        await db.commit()
    except SQLAlchemyError:
        logger.exception(
            "Failed to insert device position",
            extra={"device_id": device_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update device position",
        )

    # Refresh to get the actual ts
    await db.refresh(position)

    logger.debug(
        "Device position updated",
        extra={
            "device_id": position.device_id,
            "ts": position.ts.isoformat() if position.ts else None,
        },
    )

    return position
