# db/models.py
from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, String, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION


class Base(DeclarativeBase):
    pass


class Device(Base):
    __tablename__ = "device"
    __table_args__ = {"schema": "db_schema"}

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    positions: Mapped[List["DevicePosition"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DevicePosition(Base):
    __tablename__ = "device_position"
    __table_args__ = {"schema": "db_schema"}

    device_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("db_schema.device.id", ondelete="CASCADE"),
        primary_key=True,
    )
    ts: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        primary_key=True,
        server_default=text("now()"),
        nullable=False,
    )
    x: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    y: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)

    device: Mapped[Device] = relationship(back_populates="positions")
