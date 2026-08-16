"""Sensor descriptions for Tessie Drive Stats."""

from __future__ import annotations

from .sensor_common import *  # noqa: F403

SENSORS: list[TessieSensorEntityDescription] = []  # noqa: F405

# Vehicle state, navigation, charging and software details.
SENSORS.extend(
    [
        _s("vehicle_status", "vehicle_status", lambda d: _nested(d, "status", "status"), icon="mdi:sleep", device_class=SensorDeviceClass.ENUM, options=("asleep", "waiting_for_sleep", "awake")),
        _s("odometer_current", "odometer_current", lambda d: _nested(d, "vehicle_state", "vehicle_state", "odometer"), icon="mdi:counter", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, state_class=SensorStateClass.MEASUREMENT, precision=1),
        _s("software_version", "software_version", lambda d: _nested(d, "vehicle_state", "vehicle_state", "car_version"), icon="mdi:chip", entity_category=EntityCategory.DIAGNOSTIC),
        _s("software_update_status", "software_update_status", lambda d: _nested(d, "vehicle_state", "vehicle_state", "software_update", "status"), icon="mdi:update", entity_category=EntityCategory.DIAGNOSTIC),
        _s("software_update_version", "software_update_version", lambda d: _nested(d, "vehicle_state", "vehicle_state", "software_update", "version"), icon="mdi:tag-outline", entity_category=EntityCategory.DIAGNOSTIC),
        _s("software_update_download", "software_update_download", lambda d: _nested(d, "vehicle_state", "vehicle_state", "software_update", "download_perc"), icon="mdi:download", unit=PERCENTAGE, precision=0, entity_category=EntityCategory.DIAGNOSTIC),
        _s("software_update_install", "software_update_install", lambda d: _nested(d, "vehicle_state", "vehicle_state", "software_update", "install_perc"), icon="mdi:progress-wrench", unit=PERCENTAGE, precision=0, entity_category=EntityCategory.DIAGNOSTIC),
        _s("navigation_destination", "navigation_destination", lambda d: _nested(d, "vehicle_state", "drive_state", "active_route_destination"), icon="mdi:navigation-variant"),
        _s("navigation_miles_to_arrival", "navigation_miles_to_arrival", lambda d: _nested(d, "vehicle_state", "drive_state", "active_route_miles_to_arrival"), icon="mdi:map-marker-distance", device_class=SensorDeviceClass.DISTANCE, unit=UnitOfLength.MILES, precision=1),
        _s("navigation_minutes_to_arrival", "navigation_minutes_to_arrival", lambda d: _nested(d, "vehicle_state", "drive_state", "active_route_minutes_to_arrival"), icon="mdi:clock-outline", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
        _s("navigation_traffic_delay", "navigation_traffic_delay", lambda d: _nested(d, "vehicle_state", "drive_state", "active_route_traffic_minutes_delay"), icon="mdi:traffic-light", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1),
        _s("navigation_energy_at_arrival", "navigation_energy_at_arrival", lambda d: _nested(d, "vehicle_state", "drive_state", "active_route_energy_at_arrival"), icon="mdi:battery-arrow-down", unit=PERCENTAGE, precision=0),
        _s("charging_state_current", "charging_state_current", lambda d: _nested(d, "vehicle_state", "charge_state", "charging_state"), icon="mdi:ev-plug-tesla"),
        _s("charge_rate_current", "charge_rate_current", lambda d: _nested(d, "vehicle_state", "charge_state", "charge_rate"), icon="mdi:speedometer", device_class=SensorDeviceClass.SPEED, unit=UnitOfSpeed.MILES_PER_HOUR, precision=1),
        _s("charger_power_current", "charger_power_current", lambda d: _nested(d, "vehicle_state", "charge_state", "charger_power"), icon="mdi:lightning-bolt", device_class=SensorDeviceClass.POWER, unit=UnitOfPower.KILO_WATT, precision=1),
        _s("charge_limit", "charge_limit", lambda d: _nested(d, "vehicle_state", "charge_state", "charge_limit_soc"), icon="mdi:battery-charging-80", unit=PERCENTAGE, precision=0),
        _s("time_to_full_charge", "time_to_full_charge", lambda d: _nested(d, "vehicle_state", "charge_state", "time_to_full_charge"), icon="mdi:timer-outline", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.HOURS, precision=1),
        _s("inside_temperature_current", "inside_temperature_current", lambda d: _nested(d, "vehicle_state", "climate_state", "inside_temp"), icon="mdi:car-seat", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.CELSIUS, precision=1),
        _s("outside_temperature_current", "outside_temperature_current", lambda d: _nested(d, "vehicle_state", "climate_state", "outside_temp"), icon="mdi:thermometer", device_class=SensorDeviceClass.TEMPERATURE, unit=UnitOfTemperature.CELSIUS, precision=1),
        _s("connection_status", "connection_status", lambda d: _nested(d, "vehicle_state", "vehicle_state", "connection_status"), icon="mdi:wifi", entity_category=EntityCategory.DIAGNOSTIC),
    ]
)

# Tire pressure and status.
for position, label in (("front_left", "front_left"), ("front_right", "front_right"), ("rear_left", "rear_left"), ("rear_right", "rear_right")):
    SENSORS.extend(
        [
            _s(f"tire_pressure_{position}", f"tire_pressure_{label}", lambda d, p=position: _nested(d, "tire_pressure", p), icon="mdi:car-tire-alert", device_class=SensorDeviceClass.PRESSURE, unit=UnitOfPressure.PSI, state_class=SensorStateClass.MEASUREMENT, precision=1),
            _s(f"tire_status_{position}", f"tire_status_{label}", lambda d, p=position: _nested(d, "tire_pressure", f"{p}_status"), icon="mdi:car-tire-alert", device_class=SensorDeviceClass.ENUM, options=("unknown", "low", "normal"), enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        ]
    )

# Firmware alerts and observed sleep/activity history.
SENSORS.extend(
    [
        _s("firmware_alert_count", "firmware_alert_count", lambda d: len(d.get("firmware_alerts", [])), icon="mdi:alert-circle-outline", entity_category=EntityCategory.DIAGNOSTIC),
        _s("latest_firmware_alert", "latest_firmware_alert", lambda d: _nested({"alert": latest_record(d.get("firmware_alerts", [])) or {}}, "alert", "name"), icon="mdi:alert", entity_category=EntityCategory.DIAGNOSTIC, attributes_fn=_latest_alert_attrs),
        _s("latest_firmware_alert_at", "latest_firmware_alert_at", lambda d: _timestamp(_nested({"alert": latest_record(d.get("firmware_alerts", [])) or {}}, "alert", "timestamp")), icon="mdi:clock-alert-outline", device_class=SensorDeviceClass.TIMESTAMP, entity_category=EntityCategory.DIAGNOSTIC),
        _s("observed_awake_time_today", "observed_awake_time_today", lambda d: _activity(d)["awake_minutes"], icon="mdi:car-connected", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        _s("observed_asleep_time_today", "observed_asleep_time_today", lambda d: _activity(d)["asleep_minutes"], icon="mdi:sleep", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        _s("observed_waiting_for_sleep_time_today", "observed_waiting_for_sleep_time_today", lambda d: _activity(d)["waiting_for_sleep_minutes"], icon="mdi:sleep-off", device_class=SensorDeviceClass.DURATION, unit=UnitOfTime.MINUTES, precision=1, enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        _s("observed_wakeups_today", "observed_wakeups_today", lambda d: _activity(d)["wakeups"], icon="mdi:weather-sunset-up", enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
    ]
)

# Fleet-only Supercharger invoice analytics. Remain unavailable on personal accounts.
SENSORS.extend(
    [
        _s("charging_invoice_access", "charging_invoice_access", lambda d: "available" if d.get("charging_invoice_access") else "fleet_only", icon="mdi:file-document-outline", device_class=SensorDeviceClass.ENUM, options=("available", "fleet_only"), enabled=False, entity_category=EntityCategory.DIAGNOSTIC),
        _s("supercharger_invoice_count_this_year", "supercharger_invoice_count_this_year", lambda d: len(_invoice_records(d)) if d.get("charging_invoice_access") else None, icon="mdi:receipt-text", enabled=False),
        _s("supercharger_invoice_energy_this_year", "supercharger_invoice_energy_this_year", lambda d: invoice_sum(_invoice_records(d), "energy_used") if d.get("charging_invoice_access") else None, icon="mdi:lightning-bolt-circle", device_class=SensorDeviceClass.ENERGY, unit=UnitOfEnergy.KILO_WATT_HOUR, precision=2, enabled=False),
        _s("supercharger_invoice_charging_fees_this_year", "supercharger_invoice_charging_fees_this_year", lambda d: invoice_sum(_invoice_records(d), "charging_fees") if d.get("charging_invoice_access") else None, icon="mdi:currency-usd", device_class=SensorDeviceClass.MONETARY, precision=2, invoice_currency=True, enabled=False),
        _s("supercharger_invoice_idle_fees_this_year", "supercharger_invoice_idle_fees_this_year", lambda d: invoice_sum(_invoice_records(d), "idle_fees") if d.get("charging_invoice_access") else None, icon="mdi:timer-alert-outline", device_class=SensorDeviceClass.MONETARY, precision=2, invoice_currency=True, enabled=False),
        _s("supercharger_invoice_total_cost_this_year", "supercharger_invoice_total_cost_this_year", lambda d: invoice_sum(_invoice_records(d), "total_cost") if d.get("charging_invoice_access") else None, icon="mdi:receipt-text", device_class=SensorDeviceClass.MONETARY, precision=2, invoice_currency=True, enabled=False),
        _s("last_supercharger_invoice_cost", "last_supercharger_invoice_cost", lambda d: optional_number((_latest_invoice(d) or {}).get("total_cost")), icon="mdi:receipt-text", device_class=SensorDeviceClass.MONETARY, precision=2, invoice_currency=True, enabled=False, attributes_fn=_latest_invoice_attrs),
        _s("last_supercharger_invoice_cost_per_kwh", "last_supercharger_invoice_cost_per_kwh", lambda d: optional_number((_latest_invoice(d) or {}).get("cost_per_kwh")), icon="mdi:cash-sync", precision=3, enabled=False),
    ]
)
