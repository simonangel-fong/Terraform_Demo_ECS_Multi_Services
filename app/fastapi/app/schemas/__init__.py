# schemas/__init__.py
from .device import DeviceItem
from .telemetry import TelemetryItem, TelemetryCreate

__all__ = [
    "DeviceItem",
    "TelemetryItem",
    "TelemetryCreate",
]
