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
    """Return privacy-conscious diagnostics without route/location data."""
    coordinator: TessieDriveStatsCoordinator = entry.runtime_data
    data = coordinator.data or {}
    last_drive = data.get("last_drive") or {}
    last_charge = data.get("last_charge") or {}
    last_idle = data.get("last_idle") or {}
    latest_alerts = data.get("firmware_alerts", [])

    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "drives_year_to_date": len(data.get("drives_ytd", [])),
            "charges_year_to_date": len(data.get("charges_ytd", [])),
            "idles_year_to_date": len(data.get("idles_ytd", [])),
            "battery_health_samples": len(data.get("battery_health_measurements", [])),
            "historical_state_samples_today": len(data.get("historical_states_today", [])),
            "firmware_alert_count": len(latest_alerts),
            "last_drive_path_point_count": len(data.get("last_drive_path", [])),
            "charging_invoice_access": data.get("charging_invoice_access", False),
            "charging_invoice_count": (
                len(data.get("charging_invoices", []))
                if isinstance(data.get("charging_invoices"), list)
                else None
            ),
            "boundaries": data.get("boundaries", {}),
            "cache_updated": data.get("cache_updated", {}),
            "vehicle_status": (data.get("status") or {}).get("status"),
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
                "energy_added": last_charge.get("energy_added"),
                "cost": last_charge.get("cost"),
                "is_supercharger": last_charge.get("is_supercharger"),
            },
            "last_idle": {
                "id": last_idle.get("id"),
                "started_at": last_idle.get("started_at"),
                "ended_at": last_idle.get("ended_at"),
                "energy_used": last_idle.get("energy_used"),
                "sentry_fraction": last_idle.get("sentry_fraction"),
                "climate_fraction": last_idle.get("climate_fraction"),
            },
            "battery_keys": sorted((data.get("battery") or {}).keys()),
            "consumption_keys": sorted((data.get("consumption") or {}).keys()),
            "tire_pressure_keys": sorted((data.get("tire_pressure") or {}).keys()),
        },
    }
