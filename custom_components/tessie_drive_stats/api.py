"""Minimal asynchronous client for the Tessie API."""

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
    """Normalize a token whether the user pasted the raw token or Bearer token."""
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
        """Return authorization headers."""
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }

    async def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
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

    async def async_validate_vehicle(self) -> str:
        """Validate the token/VIN and return Tessie's vehicle display name."""
        payload = await self._get("/vehicles")
        vehicles = payload.get("results", [])

        for vehicle in vehicles:
            if str(vehicle.get("vin", "")).upper() != self.vin:
                continue

            name = vehicle_name_from_payload(vehicle)
            if name:
                return name

            # The /vehicles endpoint normally includes last_state, but use the
            # dedicated state endpoint as a robust fallback for vehicle naming.
            state = await self._get(f"/{self.vin}/state")
            return vehicle_name_from_payload(state) or f"Tesla {self.vin[-6:]}"

        raise TessieVehicleNotFound(
            "The VIN was not found in the vehicles available to this Tessie token"
        )

    async def async_get_vehicle_name(self) -> str:
        """Return Tessie's current display name for the configured vehicle."""
        return await self.async_validate_vehicle()

    async def async_get_drives(
        self,
        *,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        timezone: str = "UTC",
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return drives for the configured vehicle."""
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

        payload = await self._get(f"/{self.vin}/drives", params)
        results = payload.get("results", [])
        return results if isinstance(results, list) else []

    async def async_get_charges(
        self,
        *,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        timezone: str = "UTC",
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return charging sessions for the configured vehicle."""
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

        payload = await self._get(f"/{self.vin}/charges", params)
        results = payload.get("results", [])
        return results if isinstance(results, list) else []
