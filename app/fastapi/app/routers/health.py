# app/routers/health.py
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_db, redis_client

router = APIRouter(prefix="/health", tags=["health"])

logger = logging.getLogger(__name__)

settings = get_settings()

@router.get("/", summary="App health check")
async def health() -> dict:
    """
    Basic app-level health check.
    """
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.env,
    }


@router.get("/db", summary="Database health check")
async def health_db(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Check if PostgreSQL is reachable by doing a lightweight SELECT 1.
    """
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse({"database": "reachable"})
    except Exception as exc:
        logger.exception("Database health check failed")
        detail: str | None = str(exc) if settings.debug else None
        return JSONResponse(
            status_code=503,
            content={
                "database": "unreachable",
                "detail": detail,
            },
        )


@router.get("/redis", summary="Redis health check")
async def health_redis(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Check if Redis is reachable by sending a PING.
    """
    try:
        pong = await redis_client.ping()
        return JSONResponse({"redis": "reachable","pong": pong})
    except Exception as exc:
        logger.exception("Database health check failed")
        detail: str | None = str(exc) if settings.debug else None
        return JSONResponse(
            status_code=503,
            content={
                "redis": "unreachable",
                "detail": detail,
            },
        )
