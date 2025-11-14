# main.py

from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.device import Device
from schemas.device import DeviceRead


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "This is Home"}


@app.get("/devices", response_model=list[DeviceRead])
async def list_devices(db: AsyncSession = Depends(get_db)) -> list[DeviceRead]:
    result = await db.execute(select(Device))
    devices = result.scalars().all()
    return devices
