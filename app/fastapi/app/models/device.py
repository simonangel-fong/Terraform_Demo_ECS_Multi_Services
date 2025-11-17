# app/models/device.py
from datetime import datetime
from uuid import UUID as UUID_Type

from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    Column,
    DateTime,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Device(Base):
    __tablename__ = "device"
    __table_args__ = {"schema": "db_schema"}

    id = Column(
        BigInteger,
        primary_key=True,
        # index=True,
    )

    name = Column(
        String(64),
        nullable=False,
    )

    device_uuid = Column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True, 
    )

    api_key_hash = Column(
        CHAR(64),
        nullable=False,  
    )

    tracking_enabled = Column(
        Boolean,
        nullable=False,
        server_default=text("FALSE"), 
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(), 
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    telemetry_points = relationship(
        "Telemetry",
        back_populates="device",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Device id={self.id} name={self.name} uuid={self.device_uuid}>"
