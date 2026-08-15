"""Config flow for Tessie Drive Stats."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import (
    TessieApiClient,
    TessieApiError,
    TessieAuthError,
    TessieVehicleNotFound,
    normalize_token,
)
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_UPDATE_INTERVAL,
    CONF_VIN,
    CONF_WEEK_START,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_WEEK_START,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    WEEKDAYS,
)

TOKEN_SELECTOR = TextSelector(
    TextSelectorConfig(type=TextSelectorType.PASSWORD, autocomplete="current-password")
)


def _user_schema(default_vin: str | None = None) -> vol.Schema:
    schema: dict[Any, Any] = {
        vol.Required(CONF_ACCESS_TOKEN): TOKEN_SELECTOR,
    }
    if default_vin:
        schema[vol.Required(CONF_VIN, default=default_vin)] = str
    else:
        schema[vol.Required(CONF_VIN)] = str
    return vol.Schema(schema)


class TessieDriveStatsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tessie Drive Stats."""

    VERSION = 1

    async def _validate(self, token: str, vin: str) -> dict[str, Any]:
        client = TessieApiClient(
            async_get_clientsession(self.hass),
            token,
            vin,
        )
        return await client.async_validate_vehicle()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            token = normalize_token(user_input[CONF_ACCESS_TOKEN])
            vin = user_input[CONF_VIN].strip().upper()

            try:
                vehicle = await self._validate(token, vin)
            except TessieAuthError:
                errors["base"] = "invalid_auth"
            except TessieVehicleNotFound:
                errors["base"] = "invalid_vin"
            except TessieApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(vin)
                self._abort_if_unique_id_configured()

                title = vehicle.get("display_name") or f"Tessie {vin[-6:]}"
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_ACCESS_TOKEN: token,
                        CONF_VIN: vin,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: Mapping[str, Any],
    ) -> ConfigFlowResult:
        """Start reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle reauthentication."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        vin = entry.data[CONF_VIN]

        if user_input is not None:
            token = normalize_token(user_input[CONF_ACCESS_TOKEN])
            try:
                await self._validate(token, vin)
            except TessieAuthError:
                errors["base"] = "invalid_auth"
            except TessieApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(vin)
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={CONF_ACCESS_TOKEN: token},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): TOKEN_SELECTOR}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return TessieDriveStatsOptionsFlow()


class TessieDriveStatsOptionsFlow(OptionsFlow):
    """Handle Tessie Drive Stats options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL,
            DEFAULT_UPDATE_INTERVAL,
        )
        current_week_start = self.config_entry.options.get(
            CONF_WEEK_START,
            DEFAULT_WEEK_START,
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=current_interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                    ),
                    vol.Optional(
                        CONF_WEEK_START,
                        default=current_week_start,
                    ): vol.In(WEEKDAYS),
                }
            ),
        )
