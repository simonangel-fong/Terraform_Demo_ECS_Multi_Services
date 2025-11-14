# main.py
import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.device import Device
from schemas.device import DeviceRead
from config.setting import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Device Monitoring",
    description="Device management API",
    version="1.0.0"
)


@app.get("/", response_model=dict[str, str])
async def root() -> dict[str, str]:
    """ Home """
    return {
        "message": "API is running",
        "debug": str(settings.debug),
        "env": settings.env,
        "db_url": settings.database_url,
    }


@app.get("/health", response_model=dict[str, str])
async def health_check() -> dict[str, str]:
    """ health check endpoint"""
    return {"status": "ok"}


@app.get("/devices", response_model=list[DeviceRead])
async def list_devices(db: AsyncSession = Depends(get_db)) -> list[DeviceRead]:
    """ List all devices """
    try:
        result = await db.execute(select(Device))
        devices = result.scalars().all()
        logger.info(f"Retrieved {len(devices)} devices")
        return devices
    except Exception as e:
        logger.error(f"Error listing devices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list devices")


@app.get("/devices/{device_id}", response_model=DeviceRead)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)) -> DeviceRead:
    """Get a device by ID"""
    try:
        result = await db.execute(select(Device).where(Device.id == device_id))
        device = result.scalar_one_or_none()

        # When device if no found
        if not device:
            logger.warning(f"Device not found: {device_id}")
            raise HTTPException(status_code=404, detail="Device not found")

        # return device
        logger.info(f"Get device: {device_id}")
        return device
    # http error 4XX
    except HTTPException:
        raise
    # 5XX error: handle
    except Exception as e:
        logger.error(f"Error fetching device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch device")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug   # enable if debug mode
    )
