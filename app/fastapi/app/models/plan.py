# app/models/plan.py
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as SAEnum
from .base import Base
# or your local enums.PlanCode if you keep a shared one
from ..schemas.enums import PlanCode


class Plan(Base):
    __tablename__ = "plan"

    # code: Mapped[PlanCode] = mapped_column(
    #     String,
    #     primary_key=True,
    # )

    code: Mapped[PlanCode] = mapped_column(
        SAEnum(
            PlanCode,
            name="plan_code",
            schema="db_schema",
            native_enum=True,
            create_type=False,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            validate_strings=True,
        ),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    max_devices: Mapped[int] = mapped_column(Integer, nullable=False)
    min_sample_interval_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False)
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_price_usd: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False)

    subscriptions = relationship(
        "Subscription",
        back_populates="plan",
        lazy="selectin",
    )
