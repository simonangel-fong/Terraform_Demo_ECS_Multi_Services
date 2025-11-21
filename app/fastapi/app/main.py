# app/main.py
from __future__ import annotations
import redis
import os
from fastapi import FastAPI

from .config import get_settings
from .routers import health, device, telemetry
from .config.logging import setup_logging

setup_logging()

HOSTNAME = os.getenv("HOSTNAME", "my_host")

settings = get_settings()

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
        "app": settings.app_name,
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
        response["fastapi"] = {
            "fastapi_host": HOSTNAME,
        }
        
        pgdb_cfg = settings.postgres
        response["postgres"] = {
            "host": pgdb_cfg.host,
            "port": pgdb_cfg.port,
            "db_name": pgdb_cfg.db,
            "user": pgdb_cfg.user,
        }

        rd_cfg = settings.redis
        response["redis"] = {
            "host": rd_cfg.host,
            "port": rd_cfg.port,
            "db_name": rd_cfg.db,
        }

    return response

# ============================================================
# Routers
# ============================================================
# Health check / liveness & readiness probes
app.include_router(health.router)

# Administrative device registry endpoints (UUID-based lookups)
app.include_router(device.router)

# Device-facing telemetry ingestion and listing endpoints
app.include_router(telemetry.router)

