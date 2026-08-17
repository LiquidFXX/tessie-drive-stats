"""Lifetime sensor descriptions for Tessie Drive Stats."""

from __future__ import annotations

from typing import Any

from .lifetime import (
    earliest_measurement,
    earliest_timestamp,
    measurement_delta,
    optional_sum,
    percent,
)
from .sensor_common import *  # noqa: F403

SENSORS: list[TessieSensorEntityDescription] = []  # noqa: F405


def _records(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    return value if isinstance(value, list) else []


def _lifetime_since(data: dict[str, Any], *collections: str) -> int | None:
    values = [earliest_timestamp(_records(data, collection)) for collection in collections]
    values = [value for value in values if value is not None]
    return min(values) if values else None


def _sync_timestamp(data: dict[str, Any]) -> int | None:
    sync = data.get("lifetime_synced_at")
    if not isinstance(sync, dict):
        return None
    values = [int(value) for value in sync.values() if value]
    return min(values) if values else None


def _field(record: dict[str, Any] | None, key: str) -> float | None:
    if not record:
        return None
    return optional_number(record.get(key))


def _charge_superchargers(data: dict[str, Any]) -> list[dict[str, Any]]:
    return supercharger_records(_records(data, "lifetime_charges"))


def _ap_share(data: dict[str, Any]) -> float | None:
    drives = _records(data, "lifetime_drives")
    return percent(drive_autopilot_miles(drives), drive_miles(drives))


# True vehicle-lifetime counters. lifetime_energy_used already exists in sensor_battery.py.
SENSORS.extend(
    [
        _s(
            "lifetime_odometer",
            "lifetime_odometer",
            lambda d: _nested(d, "vehicle_state", "vehicle_state", "odometer"),
            icon="mdi:counter",
            device_class=SensorDeviceClass.DISTANCE,
            unit=UnitOfLength.MILES,
            state_class=SensorStateClass.MEASUREMENT,
            precision=1,
        ),
    ]
)

# Coverage and synchronization metadata.
SENSORS.extend(
    [
        _s("recorded_lifetime_data_since", "recorded_lifetime_data_since", lambda d: _timestamp(_lifetime_since(d, "lifetime_drives", "lifetime_charges", "lifetime_idles")), icon="mdi:calendar-start", device_class=SensorDeviceClass.TIMESTAMP),
        _s("recorded_lifetime_driving_since", "recorded_lifetime_driving_since", lambda d: _timestamp(_lifetime_since(d, "lifetime_drives")), icon="mdi:car-clock", device_class=SensorDeviceClass.TIMESTAMP),
        _s("recorded_lifetime_charging_since", "recorded_lifetime_charging_since", lambda d: _timestamp(_lifetime_since(d, "lifetime_charges")), icon="mdi:ev-station", device_class=SensorDeviceClass.TIMESTAMP),
        _s("recorded_lifetime_idle_since", "recorded_lifetime_idle_since", lambda d: _timestamp(_lifetime_since(d, "lifetime_idles")), icon="mdi:power-sleep", device_class=SensorDeviceClass.TIMESTAMP),
        _s("battery_history_since", "battery_history_since", lambda d: _timestamp(_lifetime_since(d, "lifetime_battery_health")), icon="mdi:battery-clock", device_class=SensorDeviceClass.TIMESTAMP),
        _s("recorded_lifetime_last_synced", "recorded_lifetime_last_synced", lambda d: _timestamp(_sync_timestamp(d)), icon="mdi:cloud-sync-outline", device_class=SensorDeviceClass.TIMESTAMP, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
    ]
)

# Recorded lifetime driving history.
SENSORS.extend(
    [
        _s("recorded_lifetime_drives", "recorded_lifetime_drives", lambda d: drive_count(_records(d, "lifetime_drives")), icon="mdi:car-multiple"),
        _s("recorded_lifetime_miles", "recorded_lifetime_miles", lambda d: drive_miles(_records(d, "lifetime_drives")), icon="mdi:road-variant", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("recorded_lifetime_drive_time", "recorded_lifetime_drive_time", lambda d: drive_time_minutes(_records(d, "lifetime_drives")), icon="mdi:clock-outline", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
        _s("recorded_lifetime_drive_energy", "recorded_lifetime_drive_energy", lambda d: drive_energy(_records(d, "lifetime_drives")), icon="mdi:lightning-bolt", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("recorded_lifetime_efficiency", "recorded_lifetime_efficiency", lambda d: drive_efficiency(_records(d, "lifetime_drives")), icon="mdi:gauge", unit="Wh/mi", precision=0),
        _s("recorded_lifetime_ap_fsd_miles", "recorded_lifetime_ap_fsd_miles", lambda d: drive_autopilot_miles(_records(d, "lifetime_drives")), icon="mdi:steering", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("recorded_lifetime_ap_fsd_share", "recorded_lifetime_ap_fsd_share", _ap_share, icon="mdi:chart-donut", unit=PERCENTAGE, precision=1),
        _s("recorded_lifetime_average_speed", "recorded_lifetime_average_speed", lambda d: drive_average_speed(_records(d, "lifetime_drives")), icon="mdi:speedometer-medium", device_class=SensorDeviceClass.SPEED, unit=UnitOfSpeed.MILES_PER_HOUR, precision=1),
        _s("recorded_lifetime_max_speed", "recorded_lifetime_max_speed", lambda d: drive_max_speed(_records(d, "lifetime_drives")), icon="mdi:speedometer", device_class=SensorDeviceClass.SPEED, unit=UnitOfSpeed.MILES_PER_HOUR, precision=0),
        _s("recorded_lifetime_longest_drive", "recorded_lifetime_longest_drive", lambda d: longest_drive(_records(d, "lifetime_drives")), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("recorded_lifetime_rated_range_used", "recorded_lifetime_rated_range_used", lambda d: drive_sum_field(_records(d, "lifetime_drives"), "rated_range_used"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("recorded_lifetime_average_inside_temperature", "recorded_lifetime_average_inside_temperature", lambda d: drive_weighted_average(_records(d, "lifetime_drives"), "average_inside_temperature"), icon="mdi:car-seat-cooler", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.FAHRENHEIT, precision=1),
        _s("recorded_lifetime_average_outside_temperature", "recorded_lifetime_average_outside_temperature", lambda d: drive_weighted_average(_records(d, "lifetime_drives"), "average_outside_temperature"), icon="mdi:thermometer", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.FAHRENHEIT, precision=1),
    ]
)

# Recorded lifetime charging and Supercharging.
SENSORS.extend(
    [
        _s("recorded_lifetime_charge_sessions", "recorded_lifetime_charge_sessions", lambda d: len(_records(d, "lifetime_charges")), icon="mdi:ev-plug-tesla"),
        _s("recorded_lifetime_charge_energy_added", "recorded_lifetime_charge_energy_added", lambda d: optional_sum(_records(d, "lifetime_charges"), "energy_added"), icon="mdi:battery-charging", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("recorded_lifetime_charge_energy_used", "recorded_lifetime_charge_energy_used", lambda d: optional_sum(_records(d, "lifetime_charges"), "energy_used"), icon="mdi:transmission-tower-import", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("recorded_lifetime_charge_cost", "recorded_lifetime_charge_cost", lambda d: optional_sum(_records(d, "lifetime_charges"), "cost"), icon="mdi:currency-usd", device_class=SensorDeviceClass.MONETARY, precision=2, dynamic_currency=True),
        _s("recorded_lifetime_supercharger_sessions", "recorded_lifetime_supercharger_sessions", lambda d: len(_charge_superchargers(d)), icon="mdi:ev-station"),
        _s("recorded_lifetime_supercharger_energy", "recorded_lifetime_supercharger_energy", lambda d: optional_sum(_charge_superchargers(d), "energy_added"), icon="mdi:lightning-bolt-circle", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("recorded_lifetime_supercharger_cost", "recorded_lifetime_supercharger_cost", lambda d: optional_sum(_charge_superchargers(d), "cost"), icon="mdi:currency-usd", device_class=SensorDeviceClass.MONETARY, precision=2, dynamic_currency=True),
    ]
)

# Recorded lifetime idle / vampire-drain history.
SENSORS.extend(
    [
        _s("recorded_lifetime_idle_sessions", "recorded_lifetime_idle_sessions", lambda d: idle_count(_records(d, "lifetime_idles")), icon="mdi:power-sleep"),
        _s("recorded_lifetime_idle_time", "recorded_lifetime_idle_time", lambda d: idle_time_minutes(_records(d, "lifetime_idles")), icon="mdi:timer-sand", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
        _s("recorded_lifetime_idle_energy", "recorded_lifetime_idle_energy", lambda d: idle_energy(_records(d, "lifetime_idles")), icon="mdi:battery-arrow-down-outline", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("recorded_lifetime_idle_battery_used", "recorded_lifetime_idle_battery_used", lambda d: idle_battery_used(_records(d, "lifetime_idles")), icon="mdi:battery-minus", unit=PERCENTAGE, precision=1),
        _s("recorded_lifetime_idle_rated_range_used", "recorded_lifetime_idle_rated_range_used", lambda d: idle_rated_range_used(_records(d, "lifetime_idles")), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("recorded_lifetime_sentry_time", "recorded_lifetime_sentry_time", lambda d: idle_fraction_time_minutes(_records(d, "lifetime_idles"), "sentry_fraction"), icon="mdi:shield-car", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
        _s("recorded_lifetime_climate_time", "recorded_lifetime_climate_time", lambda d: idle_fraction_time_minutes(_records(d, "lifetime_idles"), "climate_fraction"), icon="mdi:fan-clock", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
    ]
)

# Recorded battery-health history across all Tessie measurements.
SENSORS.extend(
    [
        _s("recorded_lifetime_battery_measurements", "recorded_lifetime_battery_measurements", lambda d: len(_records(d, "lifetime_battery_health")), icon="mdi:chart-timeline-variant"),
        _s("recorded_lifetime_capacity_change", "recorded_lifetime_capacity_change", lambda d: measurement_delta(_records(d, "lifetime_battery_health"), "capacity"), icon="mdi:chart-line", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("recorded_lifetime_max_range_change", "recorded_lifetime_max_range_change", lambda d: measurement_delta(_records(d, "lifetime_battery_health"), "max_range"), icon="mdi:chart-line", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("recorded_lifetime_max_ideal_range_change", "recorded_lifetime_max_ideal_range_change", lambda d: measurement_delta(_records(d, "lifetime_battery_health"), "max_ideal_range"), icon="mdi:chart-line", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("oldest_battery_capacity", "oldest_battery_capacity", lambda d: _field(earliest_measurement(_records(d, "lifetime_battery_health")), "capacity"), icon="mdi:battery-clock", device_class=SensorDeviceClass.ENERGY_STORAGE, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("oldest_battery_max_range", "oldest_battery_max_range", lambda d: _field(earliest_measurement(_records(d, "lifetime_battery_health")), "max_range"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("oldest_battery_max_ideal_range", "oldest_battery_max_ideal_range", lambda d: _field(earliest_measurement(_records(d, "lifetime_battery_health")), "max_ideal_range"), icon="mdi:map-marker-star", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
    ]
)
