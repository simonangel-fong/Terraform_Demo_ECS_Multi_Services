# app/main.py
from fastapi import FastAPI
from .config.setting import settings
from .routers import health, accounts, users, plans, subscriptions, api_keys


app = FastAPI(
    title="Device Management API",
    version="0.1.0",
    description=(
        "API for managing IoT devices.\n"
    ),
)


@app.get("/", tags=["root"], summary="Service info")
async def home():
    db_cfg = settings.database
    return {
        "service": "device-management-api",
        "status": "ok",
        "environment": settings.env,
        "debug": settings.debug,
        "database": {
            "host": db_cfg.host,
            "port": db_cfg.port,
            "db_name": db_cfg.db_name,
            "user": db_cfg.user,
        },
        "docs": {
            "openapi": "/openapi.json",
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
    }


# Mount routers
app.include_router(health.router)
app.include_router(accounts.router)
app.include_router(users.router)
app.include_router(plans.router)
app.include_router(subscriptions.router)
app.include_router(api_keys.router)
