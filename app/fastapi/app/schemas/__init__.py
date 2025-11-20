# schemas/__init__.py
from .device_registry import DeviceItem
from .telemetry_event import TelemetryItem, TelemetryCreate

__all__ = [
    "DeviceItem",
    "TelemetryItem",
    "TelemetryCreate",
]
