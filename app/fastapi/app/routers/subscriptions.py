# app/routers/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.database import get_db
from ..models.subscription import Subscription
from ..schemas.subscription import SubscriptionWithPlan

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)


@router.get(
    "",
    summary="List subscriptions",
    response_model=list[SubscriptionWithPlan],
)
async def list_subscriptions(
    account_id: int | None = Query(
        default=None,
        description="Optional filter: only subscriptions for this account_id",
    ),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of subscriptions to return",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Offset for pagination",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[SubscriptionWithPlan]:
    """
    Return a paginated list of subscriptions.

    - Read-only
    - Can be filtered by `account_id`
    - Includes plan details via `plan` relationship
    """
    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .order_by(Subscription.id)
        .offset(offset)
        .limit(limit)
    )

    if account_id is not None:
        stmt = stmt.where(Subscription.account_id == account_id)

    result = await db.execute(stmt)
    subs = result.scalars().all()

    return [SubscriptionWithPlan.model_validate(s) for s in subs]


@router.get(
    "/{subscription_id}",
    summary="Get subscription by ID",
    response_model=SubscriptionWithPlan,
)
async def get_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
) -> SubscriptionWithPlan:
    """
    Get a single subscription by its ID.

    Includes plan details via `plan` relationship.
    """
    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(Subscription.id == subscription_id)
    )
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    if sub is None:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return SubscriptionWithPlan.model_validate(sub)
