# app/routers/accounts.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..models.account import Account
from ..schemas.account import AccountSummary, AccountDetail

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get(
    "",
    summary="List accounts",
    response_model=list[AccountSummary],
)
async def list_accounts(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of accounts"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
) -> list[AccountSummary]:
    stmt = (
        select(Account)
        .order_by(Account.id)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    return [AccountSummary.model_validate(a) for a in accounts]


@router.get(
    "/{account_id}",
    summary="Get account by ID",
    response_model=AccountDetail,
)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
) -> AccountDetail:
    stmt = select(Account).where(Account.id == account_id)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return AccountDetail.model_validate(account)
