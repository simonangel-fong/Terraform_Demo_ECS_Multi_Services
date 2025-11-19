# app/main.py
from __future__ import annotations
import os
from fastapi import FastAPI

from .config.setting import settings
from .routers import health, devices, telemetry
from .config.logging import setup_logging

setup_logging()

HOSTNAME = os.getenv("HOSTNAME", "my_host")

app = FastAPI(
    title="IoT Device Management API",
    version="0.1.0",
    description=(
        "Device Management API for registering IoT devices and handling their "
        "telemetry data. Device-facing endpoints authenticate using device UUIDs "
        "and API keys, while administrative endpoints are intended for internal "
        "operations and tooling."
    ),
)


# ============================================================
# Root endpoint
# ============================================================
@app.get(
    "/",
    tags=["root"],
    summary="Service status",
    description=(
        "Return basic information about the Device Management API service. "
    ),
)
async def home() -> dict:
    """
    Return basic service metadata and status.
    """
    response: dict = {
        "service": "iot-device-management-api",
        "status": "ok",
        "environment": settings.env,
        "debug": settings.debug,
        "docs": {
            "openapi": "/openapi.json",
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
    }

    if settings.debug:
        db_cfg = settings.database
        response["database"] = {
            "fastapi_host": HOSTNAME,
            "host": db_cfg.host,
            "port": db_cfg.port,
            "db_name": db_cfg.db_name,
            "user": db_cfg.user,
        }

    return response


# ============================================================
# Routers
# ============================================================
# Health check / liveness & readiness probes
app.include_router(health.router)

# Administrative device registry endpoints (UUID-based lookups)
app.include_router(devices.router)

# Device-facing telemetry ingestion and listing endpoints
app.include_router(telemetry.router)
