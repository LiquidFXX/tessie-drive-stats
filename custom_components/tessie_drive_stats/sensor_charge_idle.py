"""Sensor descriptions for Tessie Drive Stats."""

from __future__ import annotations

from .sensor_common import *  # noqa: F403

SENSORS: list[TessieSensorEntityDescription] = []  # noqa: F405

# Charging costs and Supercharger stats.
for boundary, suffix in (("today", "today"), ("week", "this_week"), ("month", "this_month"), ("year", "this_year")):
    SENSORS.extend(
        [
            _s(f"cost_{suffix}", f"cost_{suffix}", lambda d, b=boundary: cost_since(d["charges_ytd"], d["boundaries"][b]), icon="mdi:currency-usd", device_class=SensorDeviceClass.MONETARY, precision=2, dynamic_currency=True),
            _s(f"supercharger_sessions_{suffix}", f"supercharger_sessions_{suffix}", lambda d, b=boundary: supercharger_count_since(d["charges_ytd"], d["boundaries"][b]), icon="mdi:ev-station"),
            _s(f"supercharger_energy_{suffix}", f"supercharger_energy_{suffix}", lambda d, b=boundary: supercharger_energy_since(d["charges_ytd"], d["boundaries"][b]), icon="mdi:lightning-bolt-circle", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
            _s(f"supercharger_cost_{suffix}", f"supercharger_cost_{suffix}", lambda d, b=boundary: supercharger_cost_since(d["charges_ytd"], d["boundaries"][b]), icon="mdi:currency-usd", device_class=SensorDeviceClass.MONETARY, precision=2, dynamic_currency=True),
        ]
    )

SENSORS.extend(
    [
        _s("last_charge_cost", "last_charge_cost", lambda d: optional_number(_nested(d, "last_charge", "cost")), icon="mdi:currency-usd", device_class=SensorDeviceClass.MONETARY, precision=2, dynamic_currency=True),
        _s("last_charge_energy_added", "last_charge_energy_added", lambda d: optional_number(_nested(d, "last_charge", "energy_added")), icon="mdi:battery-charging", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("last_charge_location", "last_charge_location", lambda d: _nested(d, "last_charge", "saved_location") or _nested(d, "last_charge", "location"), icon="mdi:ev-station"),
        _s("last_supercharger_cost", "last_supercharger_cost", lambda d: optional_number(_nested(d, "last_supercharger", "cost")), icon="mdi:currency-usd", device_class=SensorDeviceClass.MONETARY, precision=2, dynamic_currency=True),
        _s("last_supercharger_energy_added", "last_supercharger_energy_added", lambda d: optional_number(_nested(d, "last_supercharger", "energy_added")), icon="mdi:lightning-bolt-circle", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("last_supercharger_location", "last_supercharger_location", lambda d: _nested(d, "last_supercharger", "saved_location") or _nested(d, "last_supercharger", "location"), icon="mdi:ev-station"),
    ]
)

# Idle / vampire drain.
for boundary, suffix in (("today", "today"), ("week", "this_week"), ("month", "this_month"), ("year", "this_year")):
    SENSORS.extend(
        [
            _s(f"idle_sessions_{suffix}", f"idle_sessions_{suffix}", lambda d, b=boundary: idle_count(_period_idles(d, b)), icon="mdi:car-clock"),
            _s(f"idle_time_{suffix}", f"idle_time_{suffix}", lambda d, b=boundary: idle_time_minutes(_period_idles(d, b)), icon="mdi:timer-sand", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
            _s(f"idle_energy_{suffix}", f"idle_energy_{suffix}", lambda d, b=boundary: idle_energy(_period_idles(d, b)), icon="mdi:battery-arrow-down-outline", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
            _s(f"idle_battery_used_{suffix}", f"idle_battery_used_{suffix}", lambda d, b=boundary: idle_battery_used(_period_idles(d, b)), icon="mdi:battery-minus", unit=PERCENTAGE, precision=1),
            _s(f"idle_rated_range_used_{suffix}", f"idle_rated_range_used_{suffix}", lambda d, b=boundary: idle_rated_range_used(_period_idles(d, b)), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
            _s(f"idle_sentry_time_{suffix}", f"idle_sentry_time_{suffix}", lambda d, b=boundary: idle_fraction_time_minutes(_period_idles(d, b), "sentry_fraction"), icon="mdi:shield-car", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
            _s(f"idle_climate_time_{suffix}", f"idle_climate_time_{suffix}", lambda d, b=boundary: idle_fraction_time_minutes(_period_idles(d, b), "climate_fraction"), icon="mdi:fan-clock", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
        ]
    )

SENSORS.extend(
    [
        _s("last_idle_time", "last_idle_time", lambda d: record_time_minutes(d.get("last_idle")), icon="mdi:timer-sand", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
        _s("last_idle_energy", "last_idle_energy", lambda d: record_energy(d.get("last_idle")), icon="mdi:battery-arrow-down-outline", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("last_idle_battery_used", "last_idle_battery_used", lambda d: record_battery_used(d.get("last_idle")), icon="mdi:battery-minus", unit=PERCENTAGE, precision=1),
        _s("last_idle_rated_range_used", "last_idle_rated_range_used", lambda d: optional_number(_nested(d, "last_idle", "rated_range_used")), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("last_idle_sentry_share", "last_idle_sentry_share", lambda d: record_idle_fraction_percent(d.get("last_idle"), "sentry_fraction"), icon="mdi:shield-car", unit=PERCENTAGE, precision=1),
        _s("last_idle_climate_share", "last_idle_climate_share", lambda d: record_idle_fraction_percent(d.get("last_idle"), "climate_fraction"), icon="mdi:fan", unit=PERCENTAGE, precision=1),
        _s("last_idle_location", "last_idle_location", lambda d: _nested(d, "last_idle", "location"), icon="mdi:map-marker"),
        _s("last_idle_starting_battery", "last_idle_starting_battery", lambda d: _nested(d, "last_idle", "starting_battery"), icon="mdi:battery-high", device_class=SensorDeviceClass.BATTERY, unit=PERCENTAGE, precision=0),
        _s("last_idle_ending_battery", "last_idle_ending_battery", lambda d: _nested(d, "last_idle", "ending_battery"), icon="mdi:battery-medium", device_class=SensorDeviceClass.BATTERY, unit=PERCENTAGE, precision=0),
        _s("last_idle_state_battery_level", "last_idle_state_battery_level", lambda d: _nested(d, "last_idle_state", "battery_level"), icon="mdi:battery", device_class=SensorDeviceClass.BATTERY, unit=PERCENTAGE, precision=0, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        _s("last_idle_state_range", "last_idle_state_range", lambda d: _nested(d, "last_idle_state", "battery_range"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=1, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
    ]
)

