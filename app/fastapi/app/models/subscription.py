# # models/subscription.py
# from datetime import datetime

# from sqlalchemy import (
#     Boolean,
#     DateTime,
#     ForeignKey,
#     Integer,
#     UniqueConstraint,
# )
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from .base import Base
# from .enums import PlanCode


# class Subscription(Base):
#     __tablename__ = "subscription"

#     id: Mapped[int] = mapped_column(
#         Integer, primary_key=True, autoincrement=True)

#     account_id: Mapped[int] = mapped_column(
#         ForeignKey("db_schema.account.id", ondelete="CASCADE"),
#         nullable=False,
#         unique=True,  # one subscription per account
#     )

#     plan_code: Mapped[PlanCode] = mapped_column(
#         ForeignKey("db_schema.plan.code"),
#         nullable=False,
#     )

#     started_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), nullable=False
#     )
#     canceled_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True), nullable=True
#     )
#     auto_renew: Mapped[bool] = mapped_column(
#         Boolean, nullable=False, default=True)
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), nullable=False)

#     account = relationship(
#         "Account", back_populates="subscription", lazy="joined")
#     plan = relationship("Plan", back_populates="subscriptions", lazy="joined")

#     __table_args__ = (
#         UniqueConstraint("account_id", name="uq_subscription_account"),
#     )
