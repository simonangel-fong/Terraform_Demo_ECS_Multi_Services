# schemas/plan.py
from .base import ORMModel
from .enums import PlanCode


class PlanRead(ORMModel):
    code: PlanCode
    name: str
    max_devices: int
    min_sample_interval_seconds: int
    retention_days: int
    monthly_price_usd: float
