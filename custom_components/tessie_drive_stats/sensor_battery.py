"""Sensor descriptions for Tessie Drive Stats."""

from __future__ import annotations

from .sensor_common import *  # noqa: F403

SENSORS: list[TessieSensorEntityDescription] = []  # noqa: F405

# Consumption since last charge.
SENSORS.extend(
    [
        _s("consumption_last_charge_at", "consumption_last_charge_at", lambda d: _timestamp(_nested(d, "consumption", "last_charge_at")), icon="mdi:clock-outline", device_class=SensorDeviceClass.TIMESTAMP),
        _s("distance_since_charge", "distance_since_charge", lambda d: _nested(d, "consumption", "distance_driven"), icon="mdi:road-variant", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("battery_used_since_charge", "battery_used_since_charge", lambda d: _nested(d, "consumption", "battery_percent_used"), icon="mdi:battery-minus", unit=PERCENTAGE, precision=1),
        _s("battery_used_by_driving_since_charge", "battery_used_by_driving_since_charge", lambda d: _nested(d, "consumption", "battery_percent_used_by_driving"), icon="mdi:car-battery", unit=PERCENTAGE, precision=1),
        _s("battery_used_non_driving_since_charge", "battery_used_non_driving_since_charge", lambda d: consumption_non_driving(d.get("consumption", {}), "battery_percent_used", "battery_percent_used_by_driving"), icon="mdi:battery-clock-outline", unit=PERCENTAGE, precision=1),
        _s("rated_range_used_since_charge", "rated_range_used_since_charge", lambda d: _nested(d, "consumption", "rated_range_used"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("rated_range_used_by_driving_since_charge", "rated_range_used_by_driving_since_charge", lambda d: _nested(d, "consumption", "rated_range_used_by_driving"), icon="mdi:car", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("ideal_range_used_since_charge", "ideal_range_used_since_charge", lambda d: _nested(d, "consumption", "ideal_range_used"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2, enabled=False),
        _s("ideal_range_used_by_driving_since_charge", "ideal_range_used_by_driving_since_charge", lambda d: _nested(d, "consumption", "ideal_range_used_by_driving"), icon="mdi:car", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2, enabled=False),
        _s("energy_used_since_charge", "energy_used_since_charge", lambda d: _nested(d, "consumption", "energy_used"), icon="mdi:lightning-bolt", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("energy_used_by_driving_since_charge", "energy_used_by_driving_since_charge", lambda d: _nested(d, "consumption", "energy_used_by_driving"), icon="mdi:car-electric", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("energy_used_non_driving_since_charge", "energy_used_non_driving_since_charge", lambda d: consumption_non_driving(d.get("consumption", {}), "energy_used", "energy_used_by_driving"), icon="mdi:battery-clock-outline", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("driving_energy_share_since_charge", "driving_energy_share_since_charge", lambda d: consumption_driving_share(d.get("consumption", {})), icon="mdi:chart-donut", unit=PERCENTAGE, precision=1),
    ]
)

# Current battery telemetry.
SENSORS.extend(
    [
        _s("battery_level_current", "battery_level_current", lambda d: _nested(d, "battery", "battery_level"), icon="mdi:battery", device_class=SensorDeviceClass.BATTERY, unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("battery_range_current", "battery_range_current", lambda d: _nested(d, "battery", "battery_range"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("ideal_battery_range_current", "ideal_battery_range_current", lambda d: _nested(d, "battery", "ideal_battery_range"), icon="mdi:map-marker-star", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("phantom_drain", "phantom_drain", lambda d: _nested(d, "battery", "phantom_drain_percent"), icon="mdi:ghost", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("energy_remaining", "energy_remaining", lambda d: _nested(d, "battery", "energy_remaining"), icon="mdi:battery-charging", device_class=SensorDeviceClass.ENERGY_STORAGE, unit=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.MEASUREMENT, precision=2),
        _s("lifetime_energy_used", "lifetime_energy_used", lambda d: _nested(d, "battery", "lifetime_energy_used"), icon="mdi:counter", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=1),
        _s("pack_current", "pack_current", lambda d: _nested(d, "battery", "pack_current"), icon="mdi:current-dc", device_class=SensorDeviceClass.CURRENT, unit=UnitOfElectricCurrent.AMPERE, state_class=SensorStateClass.MEASUREMENT, precision=1, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        _s("pack_voltage", "pack_voltage", lambda d: _nested(d, "battery", "pack_voltage"), icon="mdi:sine-wave", device_class=SensorDeviceClass.VOLTAGE, unit=UnitOfElectricPotential.VOLT, state_class=SensorStateClass.MEASUREMENT, precision=1, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        _s("battery_module_temp_min", "battery_module_temp_min", lambda d: _nested(d, "battery", "module_temp_min"), icon="mdi:thermometer-low", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("battery_module_temp_max", "battery_module_temp_max", lambda d: _nested(d, "battery", "module_temp_max"), icon="mdi:thermometer-high", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("battery_module_temp_spread", "battery_module_temp_spread", lambda d: (None if optional_number(_nested(d, "battery", "module_temp_min")) is None or optional_number(_nested(d, "battery", "module_temp_max")) is None else round(float(_nested(d, "battery", "module_temp_max")) - float(_nested(d, "battery", "module_temp_min")), 1)), icon="mdi:thermometer-lines", unit="°C", state_class=SensorStateClass.MEASUREMENT, precision=1),
    ]
)

# Battery health summary and historical trend.
SENSORS.extend(
    [
        _s("battery_health", "battery_health", lambda d: _health_value(d, "health_percent"), icon="mdi:battery-heart-variant", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("battery_degradation", "battery_degradation", lambda d: _health_value(d, "degradation_percent"), icon="mdi:battery-alert-variant-outline", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("battery_capacity", "battery_capacity", lambda d: _health_value(d, "capacity"), icon="mdi:battery", device_class=SensorDeviceClass.ENERGY_STORAGE, unit=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.MEASUREMENT, precision=2),
        _s("battery_original_capacity", "battery_original_capacity", lambda d: _health_value(d, "original_capacity"), icon="mdi:battery-check", device_class=SensorDeviceClass.ENERGY_STORAGE, unit=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.MEASUREMENT, precision=2),
        _s("battery_max_range", "battery_max_range", lambda d: _health_value(d, "max_range"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("battery_max_ideal_range", "battery_max_ideal_range", lambda d: _health_value(d, "max_ideal_range"), icon="mdi:map-marker-star", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("battery_health_measurements_this_year", "battery_health_measurements_this_year", lambda d: len(d.get("battery_health_measurements", [])), icon="mdi:chart-timeline-variant", entity_category=EntityCategory.DIAGNOSTIC),
        _s("battery_capacity_change_30_days", "battery_capacity_change_30_days", lambda d: measurement_change(measurements_since(d.get("battery_health_measurements", []), d["boundaries"]["thirty_days_ago"]), "capacity"), icon="mdi:chart-line", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("battery_capacity_change_this_year", "battery_capacity_change_this_year", lambda d: measurement_change(d.get("battery_health_measurements", []), "capacity"), icon="mdi:chart-line", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("battery_max_range_change_30_days", "battery_max_range_change_30_days", lambda d: measurement_change(measurements_since(d.get("battery_health_measurements", []), d["boundaries"]["thirty_days_ago"]), "max_range"), icon="mdi:chart-line", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("battery_max_range_change_this_year", "battery_max_range_change_this_year", lambda d: measurement_change(d.get("battery_health_measurements", []), "max_range"), icon="mdi:chart-line", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
    ]
)

