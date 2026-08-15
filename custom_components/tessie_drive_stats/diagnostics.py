"""Diagnostics support for Tessie Drive Stats."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_ACCESS_TOKEN
from .coordinator import TessieDriveStatsCoordinator

TO_REDACT = {CONF_ACCESS_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return privacy-conscious diagnostics for a config entry."""
    coordinator: TessieDriveStatsCoordinator = entry.runtime_data
    data = coordinator.data or {}
    last_drive = data.get("last_drive") or {}
    last_charge = data.get("last_charge") or {}
    last_supercharger = data.get("last_supercharger") or {}
    battery_health = data.get("battery_health") or {}

    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "drives_today": len(data.get("drives_today", [])),
            "drives_year_to_date": len(data.get("drives_ytd", [])),
            "charges_year_to_date": len(data.get("charges_ytd", [])),
            "boundaries": data.get("boundaries", {}),
            "battery_health_updated_at": data.get("battery_health_updated_at"),
            "last_drive": {
                "id": last_drive.get("id"),
                "started_at": last_drive.get("started_at"),
                "ended_at": last_drive.get("ended_at"),
                "odometer_distance": last_drive.get("odometer_distance"),
                "autopilot_distance": last_drive.get("autopilot_distance"),
                "energy_used": last_drive.get("energy_used"),
            },
            "last_charge": {
                "id": last_charge.get("id"),
                "started_at": last_charge.get("started_at"),
                "ended_at": last_charge.get("ended_at"),
                "is_supercharger": last_charge.get("is_supercharger"),
                "energy_added": last_charge.get("energy_added"),
                "cost": last_charge.get("cost"),
            },
            "last_supercharger": {
                "id": last_supercharger.get("id"),
                "started_at": last_supercharger.get("started_at"),
                "ended_at": last_supercharger.get("ended_at"),
                "energy_added": last_supercharger.get("energy_added"),
                "cost": last_supercharger.get("cost"),
            },
            "battery_health": {
                "max_range": battery_health.get("max_range"),
                "capacity": battery_health.get("capacity"),
                "original_capacity": battery_health.get("original_capacity"),
                "degradation_percent": battery_health.get("degradation_percent"),
                "health_percent": battery_health.get("health_percent"),
            },
        },
    }
