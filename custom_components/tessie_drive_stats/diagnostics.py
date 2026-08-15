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

    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "drives_today": len(data.get("drives_today", [])),
            "charges_year_to_date": len(data.get("charges_ytd", [])),
            "boundaries": data.get("boundaries", {}),
            "last_drive": {
                "id": last_drive.get("id"),
                "started_at": last_drive.get("started_at"),
                "ended_at": last_drive.get("ended_at"),
                "odometer_distance": last_drive.get("odometer_distance"),
                "energy_used": last_drive.get("energy_used"),
            },
            "last_charge": {
                "id": last_charge.get("id"),
                "started_at": last_charge.get("started_at"),
                "ended_at": last_charge.get("ended_at"),
                "energy_added": last_charge.get("energy_added"),
                "cost": last_charge.get("cost"),
            },
        },
    }
