# # app/routers/plans.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from ..db.database import get_db
# from ..models.plan import Plan
# from ..schemas.plan import PlanRead

# router = APIRouter(
#     prefix="/plans",
#     tags=["plans"],
# )


# @router.get(
#     "",
#     summary="List all plans",
#     response_model=list[PlanRead],
# )
# async def list_plans(
#     db: AsyncSession = Depends(get_db),
# ) -> list[PlanRead]:
#     """
#     Return all available subscription plans.
#     """
#     stmt = select(Plan).order_by(Plan.code)
#     result = await db.execute(stmt)
#     plans = result.scalars().all()
#     return [PlanRead.model_validate(p) for p in plans]


# @router.get(
#     "/{plan_code}",
#     summary="Get plan by code",
#     response_model=PlanRead,
# )
# async def get_plan(
#     plan_code: str,
#     db: AsyncSession = Depends(get_db),
# ) -> PlanRead:
#     """
#     Get a single plan by its code (starter / pro / business / enterprise).
#     """
#     stmt = select(Plan).where(Plan.code == plan_code)
#     result = await db.execute(stmt)
#     plan = result.scalar_one_or_none()

#     if plan is None:
#         raise HTTPException(status_code=404, detail="Plan not found")

#     return PlanRead.model_validate(plan)
