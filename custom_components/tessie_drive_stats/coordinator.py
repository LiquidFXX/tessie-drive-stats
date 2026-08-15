"""Data coordinator for Tessie Drive Stats."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import TessieApiClient, TessieApiError, TessieAuthError
from .calculations import latest_record, records_since, supercharger_records
from .const import (
    CONF_UPDATE_INTERVAL,
    CONF_WEEK_START,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_WEEK_START,
    DOMAIN,
    WEEKDAYS,
)

_LOGGER = logging.getLogger(__name__)
BATTERY_HEALTH_UPDATE_INTERVAL = timedelta(hours=6)


class TessieDriveStatsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Tessie drive, charging and battery-health requests."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: TessieApiClient,
    ) -> None:
        self.api = api
        self.entry = entry
        self._battery_health: dict[str, Any] | None = None
        self._battery_health_updated_at: datetime | None = None

        update_minutes = int(
            entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{api.vin}",
            config_entry=entry,
            update_interval=timedelta(minutes=update_minutes),
            always_update=False,
        )

    def _boundaries(self) -> dict[str, int]:
        """Calculate local day/week/month/year boundaries."""
        now = dt_util.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

        week_start_name = self.entry.options.get(CONF_WEEK_START, DEFAULT_WEEK_START)
        try:
            week_start_index = WEEKDAYS.index(week_start_name)
        except ValueError:
            week_start_index = WEEKDAYS.index(DEFAULT_WEEK_START)

        days_since_week_start = (now.weekday() - week_start_index) % 7
        week_start = midnight - timedelta(days=days_since_week_start)
        month_start = midnight.replace(day=1)
        year_start = midnight.replace(month=1, day=1)

        return {
            "now": int(now.timestamp()),
            "today": int(midnight.timestamp()),
            "week": int(week_start.timestamp()),
            "month": int(month_start.timestamp()),
            "year": int(year_start.timestamp()),
        }

    async def _async_update_battery_health(
        self,
        now: datetime,
    ) -> dict[str, Any] | None:
        """Refresh slow-changing battery-health data when due."""
        refresh_due = (
            self._battery_health_updated_at is None
            or now - self._battery_health_updated_at >= BATTERY_HEALTH_UPDATE_INTERVAL
        )
        if not refresh_due:
            return self._battery_health

        try:
            self._battery_health = await self.api.async_get_battery_health()
            self._battery_health_updated_at = now
        except TessieAuthError:
            raise
        except TessieApiError as err:
            _LOGGER.warning("Unable to update Tessie battery health: %s", err)
            self._battery_health_updated_at = now

        return self._battery_health

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the data needed by all entities."""
        boundaries = self._boundaries()
        timezone = self.hass.config.time_zone
        now_dt = dt_util.now()

        try:
            drives_ytd = await self.api.async_get_drives(
                from_timestamp=boundaries["year"],
                to_timestamp=boundaries["now"],
                timezone=timezone,
            )
            drives_today = records_since(drives_ytd, boundaries["today"])

            charges_ytd = await self.api.async_get_charges(
                from_timestamp=boundaries["year"],
                to_timestamp=boundaries["now"],
                timezone=timezone,
            )

            last_drive = latest_record(drives_ytd)
            if last_drive is None:
                previous_drives = await self.api.async_get_drives(
                    timezone=timezone,
                    limit=1,
                )
                last_drive = latest_record(previous_drives)

            last_charge = latest_record(charges_ytd)
            if last_charge is None:
                previous_charges = await self.api.async_get_charges(
                    timezone=timezone,
                    limit=1,
                )
                last_charge = latest_record(previous_charges)

            last_supercharger = latest_record(supercharger_records(charges_ytd))
            if last_supercharger is None:
                previous_superchargers = await self.api.async_get_charges(
                    timezone=timezone,
                    limit=1,
                    superchargers_only=True,
                )
                last_supercharger = latest_record(previous_superchargers)

            battery_health = await self._async_update_battery_health(now_dt)

            return {
                "drives_today": drives_today,
                "drives_ytd": drives_ytd,
                "charges_ytd": charges_ytd,
                "last_drive": last_drive,
                "last_charge": last_charge,
                "last_supercharger": last_supercharger,
                "battery_health": battery_health,
                "battery_health_updated_at": (
                    int(self._battery_health_updated_at.timestamp())
                    if self._battery_health_updated_at is not None
                    else None
                ),
                "boundaries": boundaries,
            }

        except TessieAuthError as err:
            raise ConfigEntryAuthFailed("Tessie authentication failed") from err
        except TessieApiError as err:
            raise UpdateFailed(f"Error communicating with Tessie: {err}") from err
