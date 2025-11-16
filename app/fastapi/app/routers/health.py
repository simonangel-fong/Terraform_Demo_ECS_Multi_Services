# app/routers/health.py
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.setting import settings
from ..db.database import get_db

router = APIRouter(prefix="/health", tags=["health"])

logger = logging.getLogger(__name__)


@router.get("", summary="Liveness probe")
async def health() -> dict:
    """
    Health check(liveness probes).
    """
    return {"status": "ok"}


@router.get("/db", summary="Database health check")
async def health_db(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
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
