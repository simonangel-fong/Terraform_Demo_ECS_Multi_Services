# # app/routers/telemetry.py
# from datetime import datetime, timedelta, timezone

# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy import select, update
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.sql import func
# from sqlalchemy.dialects.postgresql import insert as pg_insert

# from ..db.database import get_db
# from ..models.device import Device
# from ..models.telemetry import DeviceTelemetry
# from ..models.device_latest import DeviceLatest
# from ..schemas.device_telemetry import (
#     TelemetryRead,
#     TelemetryCreate,
# )

# router = APIRouter(
#     prefix="/telemetry",
#     tags=["telemetry"],
# )

# DEFAULT_LATEST_SECONDS = 1800          # 30 minutes
# MAX_LATEST_SECONDS = 24 * 3600        # safety: 24 hours


# # ##############################
# # list telemetry
# # ##############################
# @router.get(
#     "",
#     summary="List telemetry (optionally by device, latest N seconds)",
#     response_model=list[TelemetryRead],
# )
# async def list_telemetry(
#     device_id: int | None = Query(
#         default=None,
#         description="Optional filter: only telemetry for this device_id",
#     ),
#     latest: int = Query(
#         DEFAULT_LATEST_SECONDS,
#         ge=1,
#         le=MAX_LATEST_SECONDS,
#         description=(
#             "Time window in seconds (e.g. 1800 = last 30 minutes). "
#             "Defaults to 1800. Max 86400 (24 hours)."
#         ),
#     ),
#     limit: int = Query(
#         1000,
#         ge=1,
#         le=10000,
#         description="Maximum number of telemetry rows to return",
#     ),
#     db: AsyncSession = Depends(get_db),
# ) -> list[TelemetryRead]:
#     """
#     Return telemetry rows from the last `latest` seconds.

#     - If `device_id` is provided: filter for that device only.
#     - Otherwise: returns telemetry across all devices (capped by `limit`).
#     """
#     cutoff_expr = func.now() - timedelta(seconds=latest)

#     stmt = (
#         select(DeviceTelemetry)
#         .where(DeviceTelemetry.recorded_at >= cutoff_expr)
#         .order_by(DeviceTelemetry.recorded_at.desc(), DeviceTelemetry.id.desc())
#         .limit(limit)
#     )

#     if device_id is not None:
#         stmt = stmt.where(DeviceTelemetry.device_id == device_id)

#     result = await db.execute(stmt)
#     rows = result.scalars().all()

#     return [TelemetryRead.model_validate(r) for r in rows]


# # ##############################
# # Get /telemetry/{device_id}
# # get telemetry of a device
# # ##############################
# @router.get(
#     "/{device_id}",
#     summary="List telemetry for a specific device (latest N seconds)",
#     response_model=list[TelemetryRead],
# )
# async def list_device_telemetry(
#     device_id: int,
#     latest: int = Query(
#         DEFAULT_LATEST_SECONDS,
#         ge=1,
#         le=MAX_LATEST_SECONDS,
#         description=(
#             "Time window in seconds for this device. "
#             "Defaults to 1800 (30 minutes). Max 86400 (24 hours)."
#         ),
#     ),
#     limit: int = Query(
#         1000,
#         ge=1,
#         le=10000,
#         description="Maximum number of telemetry rows to return",
#     ),
#     db: AsyncSession = Depends(get_db),
# ) -> list[TelemetryRead]:
#     """
#     Return telemetry for a specific device from the last `latest` seconds.
#     """
#     cutoff_expr = func.now() - timedelta(seconds=latest)

#     stmt = (
#         select(DeviceTelemetry)
#         .where(DeviceTelemetry.device_id == device_id)
#         .where(DeviceTelemetry.recorded_at >= cutoff_expr)
#         .order_by(DeviceTelemetry.recorded_at.desc(), DeviceTelemetry.id.desc())
#         .limit(limit)
#     )

#     result = await db.execute(stmt)
#     rows = result.scalars().all()

#     return [TelemetryRead.model_validate(r) for r in rows]


# # ##################################################
# # POST /telemetry/{device_id}
# # WRITE: single telemetry point for a device
# # ##################################################
# @router.post(
#     "/{device_id}",
#     summary="Ingest a single telemetry point for a device",
#     response_model=TelemetryRead,
#     status_code=status.HTTP_201_CREATED,
# )
# async def create_telemetry(
#     device_id: int,
#     payload: TelemetryCreate,
#     db: AsyncSession = Depends(get_db),
# ) -> TelemetryRead:
#     """
#     Insert a single telemetry row for `device_id` and update:
#     - device_telemetry
#     - device_latest (upsert)
#     - device.last_seen_at

#     NOTE:
#     - If your TelemetryCreate schema also contains device_id, you can
#       optionally validate that it matches the path param.
#     """
#     # Ensure device exists
#     device = await db.get(Device, device_id)
#     if device is None:
#         raise HTTPException(status_code=404, detail="Device not found")

#     # Optional consistency check if TelemetryCreate has device_id field:
#     if hasattr(payload, "device_id"):
#         body_device_id = getattr(payload, "device_id")
#         if body_device_id is not None and body_device_id != device_id:
#             raise HTTPException(
#                 status_code=400,
#                 detail="device_id in path and body do not match",
#             )

#     recorded_at = payload.recorded_at or datetime.now(timezone.utc)

#     telemetry = DeviceTelemetry(
#         device_id=device_id,
#         recorded_at=recorded_at,
#         x_coord=payload.x_coord,
#         y_coord=payload.y_coord,
#         meta=payload.meta,
#     )
#     db.add(telemetry)

#     stmt_latest = pg_insert(DeviceLatest).values(
#         device_id=device_id,
#         recorded_at=recorded_at,
#         x_coord=payload.x_coord,
#         y_coord=payload.y_coord,
#         meta=payload.meta or {},
#     ).on_conflict_do_update(
#         index_elements=[DeviceLatest.device_id],
#         set_={
#             "recorded_at": recorded_at,
#             "x_coord": payload.x_coord,
#             "y_coord": payload.y_coord,
#             "meta": payload.meta or {},
#         },
#         where=DeviceLatest.recorded_at < recorded_at,
#     )
#     await db.execute(stmt_latest)

#     # Update device.last_seen_at
#     await db.execute(
#         update(Device)
#         .where(Device.id == device_id)
#         .values(last_seen_at=recorded_at)
#     )

#     await db.commit()
#     await db.refresh(telemetry)

#     return TelemetryRead.model_validate(telemetry)
