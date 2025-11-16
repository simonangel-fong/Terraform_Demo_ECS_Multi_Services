# schemas/enums.py
from enum import Enum


class AccountType(str, Enum):
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class DeviceStatus(str, Enum):
    PROVISIONED = "provisioned"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RETIRED = "retired"


class PlanCode(str, Enum):
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
