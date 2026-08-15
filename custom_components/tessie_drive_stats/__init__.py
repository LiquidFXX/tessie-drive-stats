"""Tessie Drive Stats integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TessieApiClient, TessieApiError
from .const import CONF_ACCESS_TOKEN, CONF_VEHICLE_NAME, CONF_VIN
from .coordinator import TessieDriveStatsCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


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
        _LOGGER.warning(
            "Unable to refresh Tessie vehicle name during migration: %s",
            err,
        )
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
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
