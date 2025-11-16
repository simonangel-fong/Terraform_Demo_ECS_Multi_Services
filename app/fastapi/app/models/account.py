# models/account.py
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import CITEXT

from .base import Base
from .enums import AccountType


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        Enum(
            AccountType,
            name="account_type",
            schema="db_schema",
            create_type=False, 
        ),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        CITEXT(), nullable=False, unique=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # # Relationships
    # users = relationship(
    #     "User",
    #     back_populates="account",
    #     cascade="all, delete-orphan",
    #     lazy="selectin",
    # )
    # subscription = relationship(
    #     "Subscription",
    #     back_populates="account",
    #     uselist=False,
    #     lazy="selectin",
    # )
    # api_keys = relationship(
    #     "ApiKey",
    #     back_populates="account",
    #     cascade="all, delete-orphan",
    #     lazy="selectin",
    # )
    # devices = relationship(
    #     "Device",
    #     back_populates="account",
    #     cascade="all, delete-orphan",
    #     lazy="selectin",
    # )

    __table_args__ = (
        Index("idx_account_type", "account_type"),
    )
