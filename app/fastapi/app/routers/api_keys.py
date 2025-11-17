# app/routers/api_keys.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..models.api_key import ApiKey
from ..schemas.api_key import ApiKeyRead

router = APIRouter(
    prefix="/api-keys",
    tags=["api_keys"],
)


@router.get(
    "",
    summary="List API keys",
    response_model=list[ApiKeyRead],
)
async def list_api_keys(
    account_id: int | None = Query(
        default=None,
        description="Optional filter: only API keys for this account_id",
    ),
    is_active: bool | None = Query(
        default=None,
        description="Optional filter: only active/inactive API keys",
    ),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of API keys to return",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Offset for pagination",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[ApiKeyRead]:
    """
    Return a paginated list of API keys.

    Read-only:
    - `key_hash` is never exposed.
    - Optional filters by `account_id` and `is_active`.
    """
    stmt = (
        select(ApiKey)
        .order_by(ApiKey.id)
        .offset(offset)
        .limit(limit)
    )

    if account_id is not None:
        stmt = stmt.where(ApiKey.account_id == account_id)

    if is_active is not None:
        stmt = stmt.where(ApiKey.is_active == is_active)

    result = await db.execute(stmt)
    keys = result.scalars().all()

    return [ApiKeyRead.model_validate(k) for k in keys]


@router.get(
    "/{api_key_id}",
    summary="Get API key by ID",
    response_model=ApiKeyRead,
)
async def get_api_key(
    api_key_id: int,
    db: AsyncSession = Depends(get_db),
) -> ApiKeyRead:
    """
    Get a single API key by its ID.

    Read-only: `key_hash` is not returned.
    """
    stmt = select(ApiKey).where(ApiKey.id == api_key_id)
    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()

    if api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")

    return ApiKeyRead.model_validate(api_key)
