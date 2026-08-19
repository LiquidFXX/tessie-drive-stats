"""Tessie Drive Stats integration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import TessieApiClient, TessieApiError
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_VEHICLE_NAME,
    CONF_VIN,
    DOMAIN,
    FRONTEND_URL,
    FRONTEND_VERSION,
)
from .coordinator import TessieDriveStatsCoordinator

CONFIG_SCHEMA: Final = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]
_LOGGER = logging.getLogger(__name__)
_FRONTEND_DIR = Path(__file__).parent / "www"
_FRONTEND_REGISTERED = "tessie_drive_stats_frontend_registered"


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Publish and register the bundled dashboard card exactly once."""
    if hass.data.get(_FRONTEND_REGISTERED):
        return

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                f"/{DOMAIN}",
                str(_FRONTEND_DIR),
                False,
            )
        ]
    )
    add_extra_js_url(hass, f"{FRONTEND_URL}?v={FRONTEND_VERSION}")
    hass.data[_FRONTEND_REGISTERED] = True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up integration-level resources."""
    await _async_register_frontend(hass)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate older entries to store Tessie's vehicle display name."""
    if entry.version >= 2:
        return True

    vin = entry.data[CONF_VIN]
    api = TessieApiClient(
        async_get_clientsession(hass),
        entry.data[CONF_ACCESS_TOKEN],
        vin,
    )
    try:
        vehicle_name = await api.async_get_vehicle_name()
    except TessieApiError as err:
        _LOGGER.warning("Unable to refresh Tessie vehicle name during migration: %s", err)
        vehicle_name = entry.title or f"Tesla {vin[-6:]}"

    data = {**entry.data, CONF_VEHICLE_NAME: vehicle_name}
    hass.config_entries.async_update_entry(
        entry,
        data=data,
        title=vehicle_name,
        version=2,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tessie Drive Stats from a config entry."""
    # Keep this fallback in addition to integration-level async_setup. It is
    # idempotent and protects installations where startup ordering differs.
    await _async_register_frontend(hass)

    api = TessieApiClient(
        async_get_clientsession(hass),
        entry.data[CONF_ACCESS_TOKEN],
        entry.data[CONF_VIN],
    )
    coordinator = TessieDriveStatsCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
