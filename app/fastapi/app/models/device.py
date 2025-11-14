from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ''' base class for all ORM models '''
    pass


class Device(Base):
    __tablename__ = "device"                        # table name
    __table_args__ = {"schema": "db_schema"}        # schema

    # id column
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),                      # data type
        primary_key=True,                           # pk
        server_default=text("gen_random_uuid()"),   # default
    )

    name: Mapped[str] = mapped_column(
        String(255),                                # data type
        nullable=False                              # not null
    )
    type: Mapped[str] = mapped_column(
        String(100),                                # data type
        nullable=False                              # not null
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),                   # data type
        nullable=False,                             # not null
        server_default=text("now()"),               # default
    )

    def __repr__(self) -> str:
        return f"<Device id={self.id} name={self.name!r} type={self.type!r}>"
