# # models/device.py
# from datetime import datetime

# from sqlalchemy import (
#     Boolean,
#     DateTime,
#     ForeignKey,
#     Integer,
#     String,
#     Index,
# )
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy.dialects.postgresql import JSONB

# from .base import Base
# from .enums import DeviceStatus


# class Device(Base):
#     __tablename__ = "device"

#     id: Mapped[int] = mapped_column(
#         Integer, primary_key=True, autoincrement=True)

#     account_id: Mapped[int] = mapped_column(
#         ForeignKey("db_schema.account.id", ondelete="CASCADE"),
#         nullable=False,
#     )

#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     type: Mapped[str] = mapped_column(String(100), nullable=False)
#     model: Mapped[str | None] = mapped_column(String(100), nullable=True)

#     status: Mapped[DeviceStatus] = mapped_column(
#         # or Enum(DeviceStatus, name="device_status", schema="db_schema", create_type=False)
#         String,
#         nullable=False,
#         default=DeviceStatus.PROVISIONED.value,
#     )

#     firmware_version: Mapped[str | None] = mapped_column(String, nullable=True)
#     tags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
#     last_seen_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True), nullable=True
#     )
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), nullable=False)
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), nullable=False)

#     account = relationship("Account", back_populates="devices", lazy="joined")
#     telemetry = relationship(
#         "DeviceTelemetry",
#         back_populates="device",
#         cascade="all, delete-orphan",
#         lazy="selectin",
#     )
#     latest = relationship(
#         "DeviceLatest",
#         back_populates="device",
#         uselist=False,
#         lazy="joined",
#     )

#     __table_args__ = (
#         # UNIQUE (account_id, name)
#         # name from DDL: uq_device_name_per_account
#         # we don't need to re-name if we don't care; but it's fine to match
#         Index("idx_device_account_type_name", "account_id", "type", "name"),
#         Index("idx_device_account_status", "account_id", "status"),
#     )
