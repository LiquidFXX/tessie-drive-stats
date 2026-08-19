"""Efficiency-intelligence sensors for Tessie Drive Stats."""

from __future__ import annotations

from typing import Any

from .efficiency import efficiency_intelligence
from .sensor_common import *  # noqa: F403


def _intel(data: dict[str, Any]) -> dict[str, Any]:
    return efficiency_intelligence(data)


def _value(data: dict[str, Any], key: str) -> Any:
    return _intel(data).get(key)


def _band_label(value: Any) -> str | None:
    labels = {
        "below_40_f": "Below 40°F",
        "40_to_60_f": "40–60°F",
        "60_to_75_f": "60–75°F",
        "75_to_90_f": "75–90°F",
        "90_f_and_above": "90°F and above",
        "low_speed_below_25_mph": "Low speed (<25 mph)",
        "mixed_25_to_45_mph": "Mixed (25–45 mph)",
        "highway_45_mph_and_above": "Highway (45+ mph)",
    }
    return labels.get(value) if value is not None else None


def _context_label(value: Any) -> str | None:
    labels = {
        "much_better_than_typical": "Much better than typical",
        "better_than_typical": "Better than typical",
        "typical": "Typical",
        "higher_than_typical": "Higher than typical",
        "much_higher_than_typical": "Much higher than typical",
        "insufficient_data": "Insufficient data",
    }
    return labels.get(value) if value is not None else None


SENSORS: list[TessieSensorEntityDescription] = [  # noqa: F405
    _s("last_drive_efficiency_30_day_average", "last_drive_efficiency_30_day_average", lambda d: _value(d, "recent_30_day_efficiency"), icon="mdi:gauge", unit="Wh/mi", state_class=SensorStateClass.MEASUREMENT, precision=0),
    _s("last_drive_efficiency_vs_30_day", "last_drive_efficiency_vs_30_day", lambda d: _value(d, "vs_30_day_percent"), icon="mdi:compare-horizontal", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=1),
    _s("last_drive_efficiency_30_day_drives", "last_drive_efficiency_30_day_drives", lambda d: _value(d, "recent_30_day_drives"), icon="mdi:counter", state_class=SensorStateClass.MEASUREMENT),
    _s("last_drive_similar_temperature_efficiency", "last_drive_similar_temperature_efficiency", lambda d: _value(d, "similar_temperature_efficiency"), icon="mdi:thermometer-auto", unit="Wh/mi", state_class=SensorStateClass.MEASUREMENT, precision=0),
    _s("last_drive_efficiency_vs_similar_temperature", "last_drive_efficiency_vs_similar_temperature", lambda d: _value(d, "vs_similar_temperature_percent"), icon="mdi:thermometer-chevron-up", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=1),
    _s("last_drive_similar_temperature_drives", "last_drive_similar_temperature_drives", lambda d: _value(d, "similar_temperature_drives"), icon="mdi:counter", state_class=SensorStateClass.MEASUREMENT),
    _s("last_drive_similar_speed_efficiency", "last_drive_similar_speed_efficiency", lambda d: _value(d, "similar_speed_efficiency"), icon="mdi:speedometer-medium", unit="Wh/mi", state_class=SensorStateClass.MEASUREMENT, precision=0),
    _s("last_drive_efficiency_vs_similar_speed", "last_drive_efficiency_vs_similar_speed", lambda d: _value(d, "vs_similar_speed_percent"), icon="mdi:speedometer", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=1),
    _s("last_drive_similar_speed_drives", "last_drive_similar_speed_drives", lambda d: _value(d, "similar_speed_drives"), icon="mdi:counter", state_class=SensorStateClass.MEASUREMENT),
    _s("last_drive_efficiency_percentile", "last_drive_efficiency_percentile", lambda d: _value(d, "efficiency_percentile"), icon="mdi:percent-outline", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=1),
    _s("last_drive_temperature_band", "last_drive_temperature_band", lambda d: _band_label(_value(d, "temperature_band")), icon="mdi:thermometer-lines"),
    _s("last_drive_temperature_band_efficiency", "last_drive_temperature_band_efficiency", lambda d: _value(d, "temperature_band_efficiency"), icon="mdi:gauge", unit="Wh/mi", state_class=SensorStateClass.MEASUREMENT, precision=0),
    _s("last_drive_temperature_band_drives", "last_drive_temperature_band_drives", lambda d: _value(d, "temperature_band_drives"), icon="mdi:counter", state_class=SensorStateClass.MEASUREMENT),
    _s("best_temperature_band", "best_temperature_band", lambda d: _band_label(_value(d, "best_temperature_band")), icon="mdi:thermometer-check"),
    _s("best_temperature_band_efficiency", "best_temperature_band_efficiency", lambda d: _value(d, "best_temperature_band_efficiency"), icon="mdi:gauge-low", unit="Wh/mi", precision=0),
    _s("worst_temperature_band", "worst_temperature_band", lambda d: _band_label(_value(d, "worst_temperature_band")), icon="mdi:thermometer-alert"),
    _s("worst_temperature_band_efficiency", "worst_temperature_band_efficiency", lambda d: _value(d, "worst_temperature_band_efficiency"), icon="mdi:gauge-full", unit="Wh/mi", precision=0),
    _s("last_drive_speed_band", "last_drive_speed_band", lambda d: _band_label(_value(d, "speed_band")), icon="mdi:speedometer-medium"),
    _s("last_drive_speed_band_efficiency", "last_drive_speed_band_efficiency", lambda d: _value(d, "speed_band_efficiency"), icon="mdi:gauge", unit="Wh/mi", state_class=SensorStateClass.MEASUREMENT, precision=0),
    _s("last_drive_speed_band_drives", "last_drive_speed_band_drives", lambda d: _value(d, "speed_band_drives"), icon="mdi:counter", state_class=SensorStateClass.MEASUREMENT),
    _s("best_speed_band", "best_speed_band", lambda d: _band_label(_value(d, "best_speed_band")), icon="mdi:speedometer-slow"),
    _s("best_speed_band_efficiency", "best_speed_band_efficiency", lambda d: _value(d, "best_speed_band_efficiency"), icon="mdi:gauge-low", unit="Wh/mi", precision=0),
    _s("worst_speed_band", "worst_speed_band", lambda d: _band_label(_value(d, "worst_speed_band")), icon="mdi:speedometer"),
    _s("worst_speed_band_efficiency", "worst_speed_band_efficiency", lambda d: _value(d, "worst_speed_band_efficiency"), icon="mdi:gauge-full", unit="Wh/mi", precision=0),
    _s("last_drive_cabin_outside_temperature_delta", "last_drive_cabin_outside_temperature_delta", lambda d: _value(d, "cabin_outside_temperature_delta"), icon="mdi:thermometer-lines", unit=UnitOfTemperature.FAHRENHEIT, state_class=SensorStateClass.MEASUREMENT, precision=1),
    _s("last_drive_efficiency_context", "last_drive_efficiency_context", lambda d: _context_label(_value(d, "context")), icon="mdi:chart-bell-curve-cumulative"),
]
