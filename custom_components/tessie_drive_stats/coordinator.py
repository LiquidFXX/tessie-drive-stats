"""Data coordinator for Tessie Drive Stats."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
import logging
from typing import Any, TypeVar

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.storage import Store
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
from .lifetime import (
    compact_battery_health,
    compact_charge,
    compact_drive,
    compact_idle,
    merge_records,
)

_LOGGER = logging.getLogger(__name__)
T = TypeVar("T")

HISTORY_UPDATE_INTERVAL = timedelta(hours=1)
ACTIVITY_UPDATE_INTERVAL = timedelta(minutes=30)
SLOW_UPDATE_INTERVAL = timedelta(hours=6)
LIFETIME_UPDATE_INTERVAL = timedelta(hours=6)
LIFETIME_FULL_REFRESH_INTERVAL = timedelta(days=30)
LIFETIME_OVERLAP = timedelta(days=2)
LIFETIME_STORAGE_VERSION = 1


class TessieDriveStatsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Tessie analytics, vehicle-state and history requests."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: TessieApiClient,
    ) -> None:
        self.api = api
        self.entry = entry
        self._cache: dict[str, Any] = {}
        self._cache_updated: dict[str, datetime] = {}
        self._path_drive_id: Any = None

        self._lifetime_store = Store(
            hass,
            LIFETIME_STORAGE_VERSION,
            f"{DOMAIN}.lifetime.{api.vin.lower()}",
        )
        self._lifetime_loaded = False
        self._lifetime_cache: dict[str, Any] = {
            "drives": {},
            "charges": {},
            "idles": {},
            "battery_health": {},
            "synced_at": {},
            "full_synced_at": {},
        }

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
        thirty_days_ago = now - timedelta(days=30)

        return {
            "now": int(now.timestamp()),
            "today": int(midnight.timestamp()),
            "week": int(week_start.timestamp()),
            "month": int(month_start.timestamp()),
            "year": int(year_start.timestamp()),
            "thirty_days_ago": int(thirty_days_ago.timestamp()),
        }

    async def _cached_optional(
        self,
        key: str,
        fetcher: Callable[[], Awaitable[T]],
        now: datetime,
        interval: timedelta | None,
        default: T,
    ) -> T:
        """Fetch optional data on cadence, preserving last good data on failure."""
        last = self._cache_updated.get(key)
        due = interval is None or last is None or now - last >= interval
        if not due:
            return self._cache.get(key, default)

        try:
            value = await fetcher()
            self._cache[key] = value
            self._cache_updated[key] = now
        except TessieAuthError:
            raise
        except TessieApiError as err:
            _LOGGER.warning("Unable to update Tessie %s: %s", key, err)
            self._cache_updated[key] = now

        return self._cache.get(key, default)

    async def _async_load_lifetime_cache(self) -> None:
        """Load persisted lifetime history cache once per coordinator lifetime."""
        if self._lifetime_loaded:
            return

        stored = await self._lifetime_store.async_load()
        if isinstance(stored, dict):
            for collection in ("drives", "charges", "idles", "battery_health"):
                value = stored.get(collection)
                if isinstance(value, dict):
                    self._lifetime_cache[collection] = value
            for key in ("synced_at", "full_synced_at"):
                value = stored.get(key)
                if isinstance(value, dict):
                    self._lifetime_cache[key] = value

        self._lifetime_loaded = True

    async def _async_lifetime_history(
        self,
        *,
        now_timestamp: int,
        timezone: str,
    ) -> dict[str, Any]:
        """Backfill and incrementally refresh privacy-minimized lifetime history."""
        await self._async_load_lifetime_cache()

        synced_at: dict[str, Any] = self._lifetime_cache["synced_at"]
        full_synced_at: dict[str, Any] = self._lifetime_cache["full_synced_at"]
        update_seconds = int(LIFETIME_UPDATE_INTERVAL.total_seconds())
        full_seconds = int(LIFETIME_FULL_REFRESH_INTERVAL.total_seconds())
        overlap_seconds = int(LIFETIME_OVERLAP.total_seconds())

        specs: list[tuple[str, Callable[[int], Awaitable[list[dict[str, Any]]]], Any]] = [
            (
                "drives",
                lambda start: self.api.async_get_drives(
                    from_timestamp=start,
                    to_timestamp=now_timestamp,
                    timezone=timezone,
                ),
                compact_drive,
            ),
            (
                "charges",
                lambda start: self.api.async_get_charges(
                    from_timestamp=start,
                    to_timestamp=now_timestamp,
                    timezone=timezone,
                ),
                compact_charge,
            ),
            (
                "idles",
                lambda start: self.api.async_get_idles(
                    from_timestamp=start,
                    to_timestamp=now_timestamp,
                    timezone=timezone,
                ),
                compact_idle,
            ),
            (
                "battery_health",
                lambda start: self.api.async_get_battery_health_measurements(
                    from_timestamp=start,
                    to_timestamp=now_timestamp,
                ),
                compact_battery_health,
            ),
        ]

        due: list[tuple[str, Callable[[int], Awaitable[list[dict[str, Any]]]], Any, int, bool]] = []
        for name, fetcher, compactor in specs:
            records = self._lifetime_cache.get(name, {})
            last_sync = int(synced_at.get(name) or 0)
            last_full = int(full_synced_at.get(name) or 0)
            full_refresh = not records or last_full <= 0 or now_timestamp - last_full >= full_seconds

            if not full_refresh and last_sync > 0 and now_timestamp - last_sync < update_seconds:
                continue

            start = 0 if full_refresh else max(0, last_sync - overlap_seconds)
            due.append((name, fetcher, compactor, start, full_refresh))

        if due:
            responses = await asyncio.gather(
                *(fetcher(start) for _, fetcher, _, start, _ in due),
                return_exceptions=True,
            )

            changed = False
            for (name, _, compactor, _, full_refresh), response in zip(due, responses, strict=True):
                if isinstance(response, TessieAuthError):
                    raise response
                if isinstance(response, TessieApiError):
                    _LOGGER.warning("Unable to update Tessie lifetime %s: %s", name, response)
                    continue
                if isinstance(response, BaseException):
                    _LOGGER.warning("Unexpected Tessie lifetime %s error: %s", name, response)
                    continue

                current = self._lifetime_cache.get(name, {})
                self._lifetime_cache[name] = merge_records(
                    current if isinstance(current, dict) else {},
                    response,
                    compactor,
                    replace=full_refresh,
                )
                synced_at[name] = now_timestamp
                if full_refresh:
                    full_synced_at[name] = now_timestamp
                changed = True

            if changed:
                await self._lifetime_store.async_save(self._lifetime_cache)

        return {
            "lifetime_drives": list(self._lifetime_cache.get("drives", {}).values()),
            "lifetime_charges": list(self._lifetime_cache.get("charges", {}).values()),
            "lifetime_idles": list(self._lifetime_cache.get("idles", {}).values()),
            "lifetime_battery_health": list(
                self._lifetime_cache.get("battery_health", {}).values()
            ),
            "lifetime_synced_at": dict(self._lifetime_cache.get("synced_at", {})),
            "lifetime_full_synced_at": dict(
                self._lifetime_cache.get("full_synced_at", {})
            ),
        }

    async def _async_last_drive_path(
        self,
        last_drive: dict[str, Any] | None,
        now: datetime,
    ) -> list[dict[str, Any]]:
        if not last_drive:
            self._cache["last_drive_path"] = []
            self._path_drive_id = None
            return []

        drive_id = last_drive.get("id") or (
            last_drive.get("started_at"),
            last_drive.get("ended_at"),
        )
        if drive_id == self._path_drive_id:
            return self._cache.get("last_drive_path", [])

        started = int(float(last_drive.get("started_at") or 0))
        ended = int(float(last_drive.get("ended_at") or 0))
        if started <= 0 or ended <= started:
            return []

        try:
            path = await self.api.async_get_driving_path(
                from_timestamp=started,
                to_timestamp=ended,
            )
            self._cache["last_drive_path"] = path
            self._cache_updated["last_drive_path"] = now
            self._path_drive_id = drive_id
            return path
        except TessieAuthError:
            raise
        except TessieApiError as err:
            _LOGGER.warning("Unable to update Tessie last drive path: %s", err)
            return self._cache.get("last_drive_path", [])

    async def _async_update_data(self) -> dict[str, Any]:
        boundaries = self._boundaries()
        timezone = self.hass.config.time_zone
        now_dt = dt_util.now()

        try:
            drives_ytd = await self.api.async_get_drives(
                from_timestamp=boundaries["year"],
                to_timestamp=boundaries["now"],
                timezone=timezone,
            )
            charges_ytd = await self.api.async_get_charges(
                from_timestamp=boundaries["year"],
                to_timestamp=boundaries["now"],
                timezone=timezone,
            )

            last_drive = latest_record(drives_ytd)
            if last_drive is None:
                last_drive = latest_record(
                    await self.api.async_get_drives(timezone=timezone, limit=1)
                )

            last_charge = latest_record(charges_ytd)
            if last_charge is None:
                last_charge = latest_record(
                    await self.api.async_get_charges(timezone=timezone, limit=1)
                )

            last_supercharger = latest_record(supercharger_records(charges_ytd))
            if last_supercharger is None:
                last_supercharger = latest_record(
                    await self.api.async_get_charges(
                        timezone=timezone,
                        limit=1,
                        superchargers_only=True,
                    )
                )

            battery = await self._cached_optional(
                "battery", self.api.async_get_battery, now_dt, None, {}
            )
            consumption = await self._cached_optional(
                "consumption", self.api.async_get_consumption, now_dt, None, {}
            )
            vehicle_state = await self._cached_optional(
                "vehicle_state", self.api.async_get_vehicle_state, now_dt, None, {}
            )
            status = await self._cached_optional(
                "status", self.api.async_get_status, now_dt, None, {}
            )
            tire_pressure = await self._cached_optional(
                "tire_pressure", self.api.async_get_tire_pressure, now_dt, None, {}
            )
            last_idle_state = await self._cached_optional(
                "last_idle_state", self.api.async_get_last_idle_state, now_dt, None, {}
            )

            async def fetch_idles() -> list[dict[str, Any]]:
                idles = await self.api.async_get_idles(
                    from_timestamp=boundaries["year"],
                    to_timestamp=boundaries["now"],
                    timezone=timezone,
                )
                if not idles:
                    previous = await self.api.async_get_idles(timezone=timezone, limit=1)
                    if previous:
                        self._cache["last_idle_fallback"] = latest_record(previous)
                return idles

            idles_ytd = await self._cached_optional(
                "idles_ytd", fetch_idles, now_dt, HISTORY_UPDATE_INTERVAL, []
            )
            last_idle = latest_record(idles_ytd) or self._cache.get("last_idle_fallback")

            historical_states = await self._cached_optional(
                "historical_states_today",
                lambda: self.api.async_get_states(
                    from_timestamp=boundaries["today"],
                    to_timestamp=boundaries["now"],
                    timezone=timezone,
                    interval=300,
                ),
                now_dt,
                ACTIVITY_UPDATE_INTERVAL,
                [],
            )
            firmware_alerts = await self._cached_optional(
                "firmware_alerts",
                self.api.async_get_firmware_alerts,
                now_dt,
                HISTORY_UPDATE_INTERVAL,
                [],
            )

            battery_health = await self._cached_optional(
                "battery_health",
                self.api.async_get_battery_health,
                now_dt,
                SLOW_UPDATE_INTERVAL,
                None,
            )
            battery_health_measurements = await self._cached_optional(
                "battery_health_measurements",
                lambda: self.api.async_get_battery_health_measurements(
                    from_timestamp=boundaries["year"],
                    to_timestamp=boundaries["now"],
                ),
                now_dt,
                SLOW_UPDATE_INTERVAL,
                [],
            )
            charging_invoices = await self._cached_optional(
                "charging_invoices",
                lambda: self.api.async_get_charging_invoices(
                    from_timestamp=boundaries["year"],
                    to_timestamp=boundaries["now"],
                    timezone=timezone,
                ),
                now_dt,
                SLOW_UPDATE_INTERVAL,
                None,
            )

            lifetime = await self._async_lifetime_history(
                now_timestamp=boundaries["now"],
                timezone=timezone,
            )
            last_drive_path = await self._async_last_drive_path(last_drive, now_dt)

            return {
                "drives_today": records_since(drives_ytd, boundaries["today"]),
                "drives_ytd": drives_ytd,
                "charges_ytd": charges_ytd,
                "idles_ytd": idles_ytd,
                "last_drive": last_drive,
                "last_charge": last_charge,
                "last_supercharger": last_supercharger,
                "last_idle": last_idle,
                "last_idle_state": last_idle_state,
                "last_drive_path": last_drive_path,
                "battery": battery,
                "battery_health": battery_health,
                "battery_health_measurements": battery_health_measurements,
                "consumption": consumption,
                "vehicle_state": vehicle_state,
                "status": status,
                "tire_pressure": tire_pressure,
                "historical_states_today": historical_states,
                "firmware_alerts": firmware_alerts,
                "charging_invoices": charging_invoices,
                "charging_invoice_access": charging_invoices is not None,
                "boundaries": boundaries,
                "cache_updated": {
                    key: int(value.timestamp())
                    for key, value in self._cache_updated.items()
                },
                **lifetime,
            }

        except TessieAuthError as err:
            raise ConfigEntryAuthFailed("Tessie authentication failed") from err
        except TessieApiError as err:
            raise UpdateFailed(f"Error communicating with Tessie: {err}") from err
