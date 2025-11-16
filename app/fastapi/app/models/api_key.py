# # models/api_key.py
# from datetime import datetime

# from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, Index
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from .base import Base


# class ApiKey(Base):
#     __tablename__ = "api_key"

#     id: Mapped[int] = mapped_column(
#         Integer, primary_key=True, autoincrement=True)

#     account_id: Mapped[int] = mapped_column(
#         ForeignKey("db_schema.account.id", ondelete="CASCADE"),
#         nullable=False,
#     )

#     name: Mapped[str] = mapped_column(String, nullable=False)
#     key_hash: Mapped[str] = mapped_column(String, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), nullable=False)
#     last_used_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True), nullable=True
#     )
#     is_active: Mapped[bool] = mapped_column(
#         Boolean, nullable=False, default=True)

#     account = relationship("Account", back_populates="api_keys", lazy="joined")

#     __table_args__ = (
#         UniqueConstraint(
#             "account_id",
#             "name",
#             name="uq_api_key_name_per_account",
#         ),
#         UniqueConstraint("key_hash", name="uq_api_key_hash"),
#         Index("idx_api_key_account_id", "account_id"),
#         Index("idx_api_key_key_hash", "key_hash"),
#     )
