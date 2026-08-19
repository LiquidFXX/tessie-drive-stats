from custom_components.tessie_drive_stats.device_groups import (
    GROUP_BATTERY,
    GROUP_CHARGING,
    GROUP_CHARGING_ECONOMICS,
    GROUP_DRIVING,
    GROUP_EFFICIENCY,
    GROUP_IDLE,
    GROUP_LABELS,
    GROUP_LIFETIME,
    GROUP_NAVIGATION_SOFTWARE,
    GROUP_TIRES_ALERTS,
    GROUP_VEHICLE,
    binary_sensor_device_group,
    device_identifier,
    device_name,
    sensor_device_group,
)


def test_device_names_and_identifiers_are_stable():
    vin = "5YJTESTVIN"
    assert device_identifier(vin, GROUP_VEHICLE) == vin
    assert device_identifier(vin, GROUP_DRIVING) == f"{vin}:driving"
    assert device_name("My Tesla", GROUP_VEHICLE) == "My Tesla"
    assert device_name("My Tesla", GROUP_DRIVING) == "My Tesla · Driving"
    assert len(set(GROUP_LABELS.values())) == len(GROUP_LABELS)


def test_module_level_groups():
    assert sensor_device_group("drive", "miles_today") == GROUP_DRIVING
    assert sensor_device_group("efficiency", "last_drive_efficiency_context") == GROUP_EFFICIENCY
    assert sensor_device_group("charging_economics", "charging_loss_this_month") == GROUP_CHARGING_ECONOMICS
    assert sensor_device_group("lifetime", "recorded_lifetime_miles") == GROUP_LIFETIME


def test_charge_idle_groups():
    assert sensor_device_group("charge_idle", "cost_this_month") == GROUP_CHARGING
    assert sensor_device_group("charge_idle", "last_charge_cost") == GROUP_CHARGING
    assert sensor_device_group("charge_idle", "idle_energy_today") == GROUP_IDLE
    assert sensor_device_group("charge_idle", "last_idle_energy") == GROUP_IDLE


def test_battery_groups():
    assert sensor_device_group("battery", "battery_level_current") == GROUP_VEHICLE
    assert sensor_device_group("battery", "battery_range_current") == GROUP_VEHICLE
    assert sensor_device_group("battery", "ideal_battery_range_current") == GROUP_VEHICLE
    assert sensor_device_group("battery", "battery_health") == GROUP_BATTERY
    assert sensor_device_group("battery", "energy_used_since_charge") == GROUP_BATTERY
    assert sensor_device_group("battery", "lifetime_energy_used") == GROUP_LIFETIME


def test_vehicle_module_groups():
    assert sensor_device_group("vehicle", "vehicle_status") == GROUP_VEHICLE
    assert sensor_device_group("vehicle", "odometer_current") == GROUP_VEHICLE
    assert sensor_device_group("vehicle", "connection_status") == GROUP_VEHICLE
    assert sensor_device_group("vehicle", "charging_state_current") == GROUP_CHARGING
    assert sensor_device_group("vehicle", "charge_limit") == GROUP_CHARGING
    assert sensor_device_group("vehicle", "time_to_full_charge") == GROUP_CHARGING
    assert sensor_device_group("vehicle", "charging_invoice_access") == GROUP_CHARGING
    assert sensor_device_group("vehicle", "tire_pressure_front_left") == GROUP_TIRES_ALERTS
    assert sensor_device_group("vehicle", "firmware_alert_count") == GROUP_TIRES_ALERTS
    assert sensor_device_group("vehicle", "navigation_destination") == GROUP_NAVIGATION_SOFTWARE
    assert sensor_device_group("vehicle", "software_version") == GROUP_NAVIGATION_SOFTWARE
    assert sensor_device_group("vehicle", "observed_awake_time_today") == GROUP_NAVIGATION_SOFTWARE


def test_binary_sensor_groups():
    assert binary_sensor_device_group("tire_pressure_low_front_left") == GROUP_TIRES_ALERTS
    assert binary_sensor_device_group("last_drive_unusually_inefficient") == GROUP_EFFICIENCY
