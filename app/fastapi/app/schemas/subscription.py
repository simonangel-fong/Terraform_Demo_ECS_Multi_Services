# schemas/subscription.py
from datetime import datetime

from .base import ORMModel
from .enums import PlanCode
from .plan import PlanRead


class SubscriptionRead(ORMModel):
    id: int
    account_id: int
    plan_code: PlanCode
    started_at: datetime
    canceled_at: datetime | None
    auto_renew: bool
    created_at: datetime
    updated_at: datetime


class SubscriptionWithPlan(SubscriptionRead):
    plan: PlanRead
