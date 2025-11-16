# schemas/account.py
from datetime import datetime

from pydantic import Field

from .base import ORMModel
from .enums import AccountType


class AccountSummary(ORMModel):
    id: int
    name: str
    account_type: AccountType
    is_active: bool


class AccountDetail(AccountSummary):
    email: str
    created_at: datetime = Field()
    updated_at: datetime = Field()
