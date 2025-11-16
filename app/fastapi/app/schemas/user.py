# schemas/user.py
from datetime import datetime

from .base import ORMModel
from .enums import UserRole


class UserRead(ORMModel):
    id: int
    account_id: int
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
