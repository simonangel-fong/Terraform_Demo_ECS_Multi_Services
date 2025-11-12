from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class Trip(Base):
    __tablename__ = "trip"
    __table_args__ = {"schema": "db_schema"}

    trip_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    start_station: Mapped[str] = mapped_column(String(255), nullable=False)
