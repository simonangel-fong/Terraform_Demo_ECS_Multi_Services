# models/device_latest.py
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base


class DeviceLatest(Base):
    __tablename__ = "device_latest"

    device_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("db_schema.device.id", ondelete="CASCADE"),
        primary_key=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    x_coord: Mapped[float] = mapped_column(Float, nullable=False)
    y_coord: Mapped[float] = mapped_column(Float, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    device = relationship("Device", back_populates="latest", lazy="joined")
