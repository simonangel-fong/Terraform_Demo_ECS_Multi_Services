# models/base.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# specify db_schema schema
metadata = MetaData(schema="db_schema")


class Base(DeclarativeBase):
    metadata = metadata
