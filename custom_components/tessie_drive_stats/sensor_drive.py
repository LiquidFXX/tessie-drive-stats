"""Sensor descriptions for Tessie Drive Stats."""

from __future__ import annotations

from .sensor_common import *  # noqa: F403

SENSORS: list[TessieSensorEntityDescription] = []  # noqa: F405

# Existing v0.2 sensors: retain keys/unique IDs.
SENSORS.extend(
    [
        _s("drives_today", "drives_today", lambda d: drive_count(d["drives_today"]), icon="mdi:car-multiple", state_class=SensorStateClass.MEASUREMENT),
        _s("miles_today", "miles_today", lambda d: drive_miles(d["drives_today"]), icon="mdi:road-variant", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, state_class=SensorStateClass.MEASUREMENT, precision=2),
        _s("energy_today", "energy_today", lambda d: drive_energy(d["drives_today"]), icon="mdi:lightning-bolt", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("drive_time_today", "drive_time_today", lambda d: drive_time_minutes(d["drives_today"]), icon="mdi:clock-outline", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("efficiency_today", "efficiency_today", lambda d: drive_efficiency(d["drives_today"]), icon="mdi:gauge", unit="Wh/mi", state_class=SensorStateClass.MEASUREMENT, precision=0),
        _s("battery_used_today", "battery_used_today", lambda d: drive_battery_used(d["drives_today"]), icon="mdi:battery-minus", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=0),
    ]
)

for boundary, suffix in (("today", "today"), ("week", "this_week"), ("month", "this_month"), ("year", "this_year")):
    if boundary != "today":
        SENSORS.extend(
            [
                _s(f"drives_{suffix}", f"drives_{suffix}", lambda d, b=boundary: drive_count(_period_drives(d, b)), icon="mdi:car-multiple"),
                _s(f"miles_{suffix}", f"miles_{suffix}", lambda d, b=boundary: drive_miles(_period_drives(d, b)), icon="mdi:road-variant", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
                _s(f"energy_{suffix}", f"energy_{suffix}", lambda d, b=boundary: drive_energy(_period_drives(d, b)), icon="mdi:lightning-bolt", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
                _s(f"drive_time_{suffix}", f"drive_time_{suffix}", lambda d, b=boundary: drive_time_minutes(_period_drives(d, b)), icon="mdi:clock-outline", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
                _s(f"efficiency_{suffix}", f"efficiency_{suffix}", lambda d, b=boundary: drive_efficiency(_period_drives(d, b)), icon="mdi:gauge", unit="Wh/mi", precision=0),
            ]
        )

    SENSORS.extend(
        [
            _s(f"autopilot_fsd_miles_{suffix}", f"autopilot_fsd_miles_{suffix}", lambda d, b=boundary: drive_autopilot_miles(_period_drives(d, b)), icon="mdi:steering", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
            _s(f"average_speed_{suffix}", f"average_speed_{suffix}", lambda d, b=boundary: drive_average_speed(_period_drives(d, b)), icon="mdi:speedometer-medium", device_class=SensorDeviceClass.SPEED, unit=UnitOfSpeed.MILES_PER_HOUR, precision=1),
            _s(f"max_speed_{suffix}", f"max_speed_{suffix}", lambda d, b=boundary: drive_max_speed(_period_drives(d, b)), icon="mdi:speedometer", device_class=SensorDeviceClass.SPEED, unit=UnitOfSpeed.MILES_PER_HOUR, precision=0),
            _s(f"longest_drive_{suffix}", f"longest_drive_{suffix}", lambda d, b=boundary: longest_drive(_period_drives(d, b)), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
            _s(f"rated_range_used_{suffix}", f"rated_range_used_{suffix}", lambda d, b=boundary: drive_sum_field(_period_drives(d, b), "rated_range_used"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
            _s(f"average_inside_temperature_{suffix}", f"average_inside_temperature_{suffix}", lambda d, b=boundary: drive_weighted_average(_period_drives(d, b), "average_inside_temperature"), icon="mdi:car-seat-cooler", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.FAHRENHEIT, precision=1, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
            _s(f"average_outside_temperature_{suffix}", f"average_outside_temperature_{suffix}", lambda d, b=boundary: drive_weighted_average(_period_drives(d, b), "average_outside_temperature"), icon="mdi:thermometer", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.FAHRENHEIT, precision=1, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        ]
    )

SENSORS.extend(
    [
        _s("last_drive_miles", "last_drive_miles", lambda d: record_distance(d["last_drive"]), icon="mdi:car", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, state_class=SensorStateClass.MEASUREMENT, precision=2),
        _s("last_drive_autopilot_fsd_miles", "last_drive_autopilot_fsd_miles", lambda d: record_autopilot_distance(d["last_drive"]), icon="mdi:steering", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, state_class=SensorStateClass.MEASUREMENT, precision=2),
        _s("last_drive_energy", "last_drive_energy", lambda d: record_energy(d["last_drive"]), icon="mdi:lightning-bolt", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2),
        _s("last_drive_time", "last_drive_time", lambda d: record_time_minutes(d["last_drive"]), icon="mdi:timer-outline", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("last_drive_efficiency", "last_drive_efficiency", lambda d: record_efficiency(d["last_drive"]), icon="mdi:gauge", unit="Wh/mi", state_class=SensorStateClass.MEASUREMENT, precision=0),
        _s("last_drive_start", "last_drive_start", lambda d: record_location(d["last_drive"], ending=False), icon="mdi:map-marker"),
        _s("last_drive_destination", "last_drive_destination", lambda d: record_location(d["last_drive"], ending=True), icon="mdi:map-marker-check"),
        _s("last_drive_starting_battery", "last_drive_starting_battery", lambda d: _nested(d, "last_drive", "starting_battery"), icon="mdi:battery", device_class=SensorDeviceClass.BATTERY, unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=0),
        _s("last_drive_ending_battery", "last_drive_ending_battery", lambda d: _nested(d, "last_drive", "ending_battery"), icon="mdi:battery", device_class=SensorDeviceClass.BATTERY, unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=0),
        _s("last_drive_battery_used", "last_drive_battery_used", lambda d: record_battery_used(d["last_drive"]), icon="mdi:battery-minus", unit=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, precision=0),
        _s("last_drive_average_speed", "last_drive_average_speed", lambda d: _nested(d, "last_drive", "average_speed"), icon="mdi:speedometer", device_class=SensorDeviceClass.SPEED, unit=UnitOfSpeed.MILES_PER_HOUR, state_class=SensorStateClass.MEASUREMENT, precision=0),
        _s("last_drive_max_speed", "last_drive_max_speed", lambda d: _nested(d, "last_drive", "max_speed"), icon="mdi:speedometer", device_class=SensorDeviceClass.SPEED, unit=UnitOfSpeed.MILES_PER_HOUR, state_class=SensorStateClass.MEASUREMENT, precision=0),
        _s("last_drive_inside_temperature", "last_drive_inside_temperature", lambda d: _nested(d, "last_drive", "average_inside_temperature"), icon="mdi:car-seat-cooler", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.FAHRENHEIT, precision=1),
        _s("last_drive_outside_temperature", "last_drive_outside_temperature", lambda d: _nested(d, "last_drive", "average_outside_temperature"), icon="mdi:thermometer", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.FAHRENHEIT, precision=1),
        _s("last_drive_rated_range_used", "last_drive_rated_range_used", lambda d: _nested(d, "last_drive", "rated_range_used"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=2),
        _s("last_drive_tag", "last_drive_tag", lambda d: _nested(d, "last_drive", "tag"), icon="mdi:tag-outline"),
        _s("last_drive_path_points", "last_drive_path_points", lambda d: len(d.get("last_drive_path", [])), icon="mdi:map-marker-path", entity_category=EntityCategory.DIAGNOSTIC, enabled=False, attributes_fn=_last_path_attrs),
        _s("last_drive_path_autopilot_share", "last_drive_path_autopilot_share", lambda d: path_autopilot_share(d.get("last_drive_path", [])), icon="mdi:steering", unit=PERCENTAGE, precision=1, entity_category=EntityCategory.DIAGNOSTIC, enabled=False),
    ]
)
