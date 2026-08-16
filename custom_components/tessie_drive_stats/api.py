"""Asynchronous client for the Tessie API."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import REQUEST_TIMEOUT, TESSIE_BASE_URL


class TessieApiError(Exception):
    """Base Tessie API exception."""


class TessieAuthError(TessieApiError):
    """Raised when Tessie rejects the access token."""


class TessieVehicleNotFound(TessieApiError):
    """Raised when the configured VIN is not available to the token."""


def normalize_token(token: str) -> str:
    """Normalize a token whether the user pasted raw token or Bearer token."""
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return token


def vehicle_name_from_payload(payload: dict[str, Any]) -> str | None:
    """Extract the Tesla vehicle name from supported Tessie response shapes."""
    candidates: list[Any] = [
        payload.get("display_name"),
        (payload.get("vehicle_state") or {}).get("vehicle_name"),
    ]

    last_state = payload.get("last_state") or {}
    if isinstance(last_state, dict):
        candidates.extend(
            [
                last_state.get("display_name"),
                (last_state.get("vehicle_state") or {}).get("vehicle_name"),
            ]
        )

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


class TessieApiClient:
    """Async Tessie API client using Home Assistant's shared aiohttp session."""

    def __init__(self, session: aiohttp.ClientSession, token: str, vin: str) -> None:
        self._session = session
        self._token = normalize_token(token)
        self.vin = vin.strip().upper()

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }

    async def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        allow_forbidden: bool = False,
    ) -> dict[str, Any] | None:
        """Perform a GET request and return parsed JSON."""
        url = f"{TESSIE_BASE_URL}{path}"
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with self._session.get(
                    url,
                    headers=self.headers,
                    params=params,
                ) as response:
                    payload = await response.json(content_type=None)

                    if response.status == 403 and allow_forbidden:
                        return None
                    if response.status in (401, 403):
                        raise TessieAuthError(
                            payload.get("error", "Access token rejected by Tessie")
                            if isinstance(payload, dict)
                            else "Access token rejected by Tessie"
                        )
                    if response.status >= 400:
                        detail = (
                            payload.get("error")
                            if isinstance(payload, dict)
                            else str(payload)
                        )
                        raise TessieApiError(
                            f"Tessie returned HTTP {response.status}: {detail}"
                        )
                    if not isinstance(payload, dict):
                        raise TessieApiError("Tessie returned an unexpected response")
                    return payload
        except asyncio.TimeoutError as err:
            raise TessieApiError("Timed out communicating with Tessie") from err
        except aiohttp.ClientError as err:
            raise TessieApiError(f"Error communicating with Tessie: {err}") from err

    @staticmethod
    def _results(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
        if not payload:
            return []
        results = payload.get("results", [])
        return [item for item in results if isinstance(item, dict)] if isinstance(results, list) else []

    async def async_validate_vehicle(self) -> str:
        payload = await self._get("/vehicles") or {}
        for vehicle in self._results(payload):
            if str(vehicle.get("vin", "")).upper() != self.vin:
                continue
            name = vehicle_name_from_payload(vehicle)
            if name:
                return name
            state = await self.async_get_vehicle_state()
            return vehicle_name_from_payload(state) or f"Tesla {self.vin[-6:]}"
        raise TessieVehicleNotFound(
            "The VIN was not found in the vehicles available to this Tessie token"
        )

    async def async_get_vehicle_name(self) -> str:
        return await self.async_validate_vehicle()

    async def async_get_vehicle_state(self) -> dict[str, Any]:
        return await self._get(f"/{self.vin}/state") or {}

    async def async_get_status(self) -> dict[str, Any]:
        return await self._get(f"/{self.vin}/status") or {}

    async def async_get_battery(self) -> dict[str, Any]:
        return await self._get(f"/{self.vin}/battery") or {}

    async def async_get_consumption(self) -> dict[str, Any]:
        return await self._get(f"/{self.vin}/consumption_since_charge") or {}

    async def async_get_tire_pressure(self) -> dict[str, Any]:
        return await self._get(
            f"/{self.vin}/tire_pressure",
            {"pressure_format": "psi"},
        ) or {}

    async def async_get_firmware_alerts(self) -> list[dict[str, Any]]:
        return self._results(await self._get(f"/{self.vin}/firmware_alerts"))

    async def async_get_last_idle_state(self) -> dict[str, Any]:
        payload = await self._get(f"/{self.vin}/last_idle_state") or {}
        result = payload.get("result")
        return result if isinstance(result, dict) else {}

    async def async_get_drives(
        self,
        *,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        timezone: str = "UTC",
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "distance_format": "mi",
            "temperature_format": "f",
            "timezone": timezone,
            "format": "json",
        }
        if from_timestamp is not None:
            params["from"] = from_timestamp
        if to_timestamp is not None:
            params["to"] = to_timestamp
        if limit is not None:
            params["limit"] = limit
        return self._results(await self._get(f"/{self.vin}/drives", params))

    async def async_get_charges(
        self,
        *,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        timezone: str = "UTC",
        limit: int | None = None,
        superchargers_only: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "distance_format": "mi",
            "timezone": timezone,
            "format": "json",
        }
        if from_timestamp is not None:
            params["from"] = from_timestamp
        if to_timestamp is not None:
            params["to"] = to_timestamp
        if limit is not None:
            params["limit"] = limit
        if superchargers_only:
            params["superchargers_only"] = "true"
        return self._results(await self._get(f"/{self.vin}/charges", params))

    async def async_get_idles(
        self,
        *,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        timezone: str = "UTC",
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "distance_format": "mi",
            "timezone": timezone,
            "format": "json",
        }
        if from_timestamp is not None:
            params["from"] = from_timestamp
        if to_timestamp is not None:
            params["to"] = to_timestamp
        if limit is not None:
            params["limit"] = limit
        return self._results(await self._get(f"/{self.vin}/idles", params))

    async def async_get_states(
        self,
        *,
        from_timestamp: int,
        to_timestamp: int,
        timezone: str,
        interval: int = 300,
    ) -> list[dict[str, Any]]:
        params = {
            "from": from_timestamp,
            "to": to_timestamp,
            "interval": interval,
            "condense": "true",
            "timezone": timezone,
            "distance_format": "mi",
            "temperature_format": "f",
            "format": "json",
        }
        return self._results(await self._get(f"/{self.vin}/states", params))

    async def async_get_driving_path(
        self,
        *,
        from_timestamp: int,
        to_timestamp: int,
    ) -> list[dict[str, Any]]:
        params = {
            "from": from_timestamp,
            "to": to_timestamp,
            "simplify": "true",
            "details": "true",
        }
        return self._results(await self._get(f"/{self.vin}/path", params))

    async def async_get_battery_health(self) -> dict[str, Any] | None:
        payload = await self._get("/battery_health", {"distance_format": "mi"})
        for result in self._results(payload):
            if str(result.get("vin", "")).upper() == self.vin:
                return result
        return None

    async def async_get_battery_health_measurements(
        self,
        *,
        from_timestamp: int,
        to_timestamp: int,
    ) -> list[dict[str, Any]]:
        payload = await self._get(
            f"/{self.vin}/battery_health",
            {
                "from": from_timestamp,
                "to": to_timestamp,
                "distance_format": "mi",
            },
        ) or {}
        results = self._results(payload)
        if results:
            return results
        result = payload.get("result")
        return [result] if isinstance(result, dict) else []

    async def async_get_charging_invoices(
        self,
        *,
        from_timestamp: int,
        to_timestamp: int,
        timezone: str,
    ) -> list[dict[str, Any]] | None:
        payload = await self._get(
            "/charging_invoices",
            {
                "from": from_timestamp,
                "to": to_timestamp,
                "vin": self.vin,
                "timezone": timezone,
                "format": "json",
            },
            allow_forbidden=True,
        )
        if payload is None:
            return None
        return self._results(payload)
