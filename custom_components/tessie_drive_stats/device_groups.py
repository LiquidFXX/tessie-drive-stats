"""Device-group metadata for Tessie Drive Stats.

This module intentionally has no Home Assistant imports so the grouping rules can
be unit-tested without installing Home Assistant.
"""

from __future__ import annotations

GROUP_VEHICLE = "vehicle"
GROUP_DRIVING = "driving"
GROUP_EFFICIENCY = "efficiency"
GROUP_CHARGING = "charging"
GROUP_CHARGING_ECONOMICS = "charging_economics"
GROUP_BATTERY = "battery"
GROUP_IDLE = "idle_vampire"
GROUP_LIFETIME = "lifetime"
GROUP_TIRES_ALERTS = "tires_alerts"
GROUP_NAVIGATION_SOFTWARE = "navigation_software"

GROUP_LABELS: dict[str, str] = {
    GROUP_VEHICLE: "Vehicle",
    GROUP_DRIVING: "Driving",
    GROUP_EFFICIENCY: "Efficiency",
    GROUP_CHARGING: "Charging",
    GROUP_CHARGING_ECONOMICS: "Charging Economics",
    GROUP_BATTERY: "Battery",
    GROUP_IDLE: "Idle & Vampire",
    GROUP_LIFETIME: "Lifetime",
    GROUP_TIRES_ALERTS: "Tires & Alerts",
    GROUP_NAVIGATION_SOFTWARE: "Navigation & Software",
}

GROUP_MODELS: dict[str, str] = {
    GROUP_VEHICLE: "Vehicle analytics via Tessie",
    GROUP_DRIVING: "Driving analytics",
    GROUP_EFFICIENCY: "Efficiency analytics",
    GROUP_CHARGING: "Charging analytics",
    GROUP_CHARGING_ECONOMICS: "Charging economics analytics",
    GROUP_BATTERY: "Battery analytics",
    GROUP_IDLE: "Idle and vampire-drain analytics",
    GROUP_LIFETIME: "Lifetime analytics",
    GROUP_TIRES_ALERTS: "Tire and alert analytics",
    GROUP_NAVIGATION_SOFTWARE: "Navigation and software analytics",
}

_ALL_GROUPS = frozenset(GROUP_LABELS)


def device_identifier(vin: str, group: str) -> str:
    """Return the stable device-registry identifier for a group."""
    if group not in _ALL_GROUPS:
        raise ValueError(f"Unknown device group: {group}")
    return vin if group == GROUP_VEHICLE else f"{vin}:{group}"


def device_name(vehicle_name: str, group: str) -> str:
    """Return the Home Assistant device name for a group."""
    if group not in _ALL_GROUPS:
        raise ValueError(f"Unknown device group: {group}")
    if group == GROUP_VEHICLE:
        return vehicle_name
    return f"{vehicle_name} · {GROUP_LABELS[group]}"


def sensor_device_group(source: str, key: str) -> str:
    """Map a sensor source module/key to its analytics device group."""
    if source == "drive":
        return GROUP_DRIVING
    if source == "efficiency":
        return GROUP_EFFICIENCY
    if source == "charging_economics":
        return GROUP_CHARGING_ECONOMICS
    if source == "lifetime":
        return GROUP_LIFETIME

    if source == "charge_idle":
        if key.startswith("idle_") or key.startswith("last_idle_"):
            return GROUP_IDLE
        return GROUP_CHARGING

    if source == "battery":
        if key in {
            "battery_level_current",
            "battery_range_current",
            "ideal_battery_range_current",
        }:
            return GROUP_VEHICLE
        if key == "lifetime_energy_used":
            return GROUP_LIFETIME
        return GROUP_BATTERY

    if source == "vehicle":
        if (
            key.startswith("tire_")
            or key.startswith("firmware_")
            or key.startswith("latest_firmware_")
        ):
            return GROUP_TIRES_ALERTS

        if (
            key.startswith("navigation_")
            or key.startswith("software_")
            or key.startswith("observed_")
        ):
            return GROUP_NAVIGATION_SOFTWARE

        if (
            key.startswith("charging_")
            or key.startswith("charge_")
            or key.startswith("charger_")
            or key.startswith("supercharger_invoice_")
            or key.startswith("last_supercharger_invoice_")
            or key == "time_to_full_charge"
        ):
            return GROUP_CHARGING

        return GROUP_VEHICLE

    raise ValueError(f"Unknown sensor source: {source}")


def binary_sensor_device_group(key: str) -> str:
    """Map a binary-sensor key to its analytics device group."""
    if key.startswith("tire_pressure_low_"):
        return GROUP_TIRES_ALERTS
    if key == "last_drive_unusually_inefficient":
        return GROUP_EFFICIENCY
    return GROUP_VEHICLE
