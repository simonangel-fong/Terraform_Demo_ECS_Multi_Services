# models/device_telemetry.py
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base


class DeviceTelemetry(Base):
    __tablename__ = "device_telemetry"


    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    device_id: Mapped[int] = mapped_column(
        ForeignKey("db_schema.device.id", ondelete="CASCADE"),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    x_coord: Mapped[float] = mapped_column(Float, nullable=False)
    y_coord: Mapped[float] = mapped_column(Float, nullable=False)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    device = relationship("Device", back_populates="telemetry", lazy="joined")

    __table_args__ = (
        Index(
            "idx_device_telemetry_device_time",
            "device_id",
            "recorded_at",
            postgresql_using="btree",
        ),
        Index(
            "idx_device_telemetry_time_device",
            "recorded_at",
            "device_id",
            postgresql_using="btree",
        ),
    )
