# models/user.py
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import CITEXT

from .base import Base
from .enums import UserRole


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("db_schema.account.id", ondelete="CASCADE"),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(CITEXT(), nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        # Uses existing db_schema.user_role enum
        # keep column type simple, or use Enum(UserRole, ...) if you prefer
        String,
        nullable=False,
        default=UserRole.VIEWER.value,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    account = relationship("Account", back_populates="users", lazy="joined")

    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "email",
            name="uq_user_email_per_account",
        ),
    )
