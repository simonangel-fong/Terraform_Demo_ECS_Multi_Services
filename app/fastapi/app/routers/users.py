# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..models.user import User
from ..schemas.user import UserRead

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "",
    summary="List users",
    response_model=list[UserRead],
)
async def list_users(
    account_id: int | None = Query(
        default=None,
        description="Optional filter: only users for this account_id",
    ),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of users to return",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Offset for pagination",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[UserRead]:
    """
    Return a paginated list of users.

    - Read-only
    - Can be filtered by `account_id`
    """
    stmt = select(User).order_by(User.id).offset(offset).limit(limit)

    if account_id is not None:
        stmt = stmt.where(User.account_id == account_id)

    result = await db.execute(stmt)
    users = result.scalars().all()

    return [UserRead.model_validate(u) for u in users]


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    response_model=UserRead,
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """
    Get a single user by its ID.

    Password hash is never exposed in this schema.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserRead.model_validate(user)
