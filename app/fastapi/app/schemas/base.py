# schemas/base.py
from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base Pydantic model for ORM objects."""
    model_config = ConfigDict(from_attributes=True)
