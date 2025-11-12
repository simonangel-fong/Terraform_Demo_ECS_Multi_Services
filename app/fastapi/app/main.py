import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from .database import get_session, create_all
from .models import Trip
from . import schemas


app = FastAPI(title="Trip CRUD API", version="1.0.0")


# @app.on_event("startup")
# async def on_startup():
#     if os.getenv("DB_CREATE_ALL", "false").lower() in {"1", "true", "yes"}:
#         print("Startup")
#         await create_all()


@app.get("/")
def read_root():
    msg = "This is home"
    print(f"Debugging Value: {msg}")
    return {"message": msg}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/trips", response_model=List[schemas.TripOut])
async def list_trips(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Trip).order_by(Trip.trip_id))
    trips = list(result.scalars().all())
    return trips


@app.get("/trips/{trip_id}", response_model=schemas.TripOut)
async def get_trip(trip_id: int, session: AsyncSession = Depends(get_session)):
    trip = await session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@app.post("/trips", response_model=schemas.TripOut, status_code=status.HTTP_201_CREATED)
async def create_trip(payload: schemas.TripCreate, session: AsyncSession = Depends(get_session)):
    trip = Trip(start_time=payload.start_time,
                start_station=payload.start_station)
    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip


@app.put("/trips/{trip_id}", response_model=schemas.TripOut)
async def update_trip(trip_id: int, payload: schemas.TripUpdate, session: AsyncSession = Depends(get_session)):
    trip = await session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    if payload.start_time is not None:
        trip.start_time = payload.start_time
    if payload.start_station is not None:
        trip.start_station = payload.start_station

    await session.commit()
    await session.refresh(trip)
    return trip


@app.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(trip_id: int, session: AsyncSession = Depends(get_session)):
    trip = await session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    await session.delete(trip)
    await session.commit()
    return None
