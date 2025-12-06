"""Config flow for Netzero Energy."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client
from homeassistant.util import dt as dt_util

from .api import NetzeroApiAuthError, NetzeroApiClient, NetzeroApiError
from .const import (
    CONF_APP_VERSION,
    CONF_BASE_URL,
    CONF_BEARER_TOKEN,
    CONF_FLEET_BASE_URL,
    CONF_NETZERO_TOKEN,
    CONF_SITE_ID,
    CONF_UPDATE_INTERVAL,
    CONF_USER_ID,
    DEFAULT_APP_VERSION,
    DEFAULT_BASE_URL,
    DEFAULT_FLEET_BASE_URL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SITE_ID): str,
        vol.Required(CONF_BEARER_TOKEN): str,
        vol.Required(CONF_NETZERO_TOKEN): str,
        vol.Optional(CONF_USER_ID): str,
        vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
        vol.Optional(CONF_FLEET_BASE_URL, default=DEFAULT_FLEET_BASE_URL): str,
        vol.Optional(CONF_APP_VERSION, default=DEFAULT_APP_VERSION): str,
    }
)


class NetzeroConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Netzero Energy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors=errors,
            )

        await self.async_set_unique_id(user_input[CONF_SITE_ID])
        self._abort_if_unique_id_configured()

        # Try a quick connectivity check
        session = aiohttp_client.async_get_clientsession(self.hass)
        api = NetzeroApiClient(
            session=session,
            base_url=user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL),
            fleet_base_url=user_input.get(CONF_FLEET_BASE_URL, DEFAULT_FLEET_BASE_URL),
            bearer_token=user_input[CONF_BEARER_TOKEN],
            netzero_token=user_input[CONF_NETZERO_TOKEN],
            user_id=user_input.get(CONF_USER_ID),
            site_id=user_input[CONF_SITE_ID],
            app_version=user_input.get(CONF_APP_VERSION, DEFAULT_APP_VERSION),
        )
        now = dt_util.as_local(dt_util.utcnow())
        start = dt_util.start_of_local_day(now)
        end = start + timedelta(minutes=5)
        try:
            await api.async_get_telemetry_history(
                str(start.tzinfo) if start.tzinfo else "UTC",
                start,
                end,
            )
        except NetzeroApiAuthError:
            errors["base"] = "invalid_auth"
        except NetzeroApiError:
            errors["base"] = "cannot_connect"
        except Exception:  # noqa: BLE001
            errors["base"] = "unknown"

        if errors:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors=errors,
            )

        return self.async_create_entry(title=f"Netzero {user_input[CONF_SITE_ID]}", data=user_input)

    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        """Import via YAML not supported; defer to UI."""
        return await self.async_step_user(user_input)

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return NetzeroOptionsFlowHandler(config_entry)


class NetzeroOptionsFlowHandler(OptionsFlow):
    """Handle Netzero options."""

    def __init__(self, entry: ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.entry.options.get(
            CONF_UPDATE_INTERVAL,
            self.entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        )
        if isinstance(current_interval, timedelta):
            current_interval = int(current_interval.total_seconds())

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=current_interval,
                    ): int,
                    vol.Optional(
                        CONF_BASE_URL,
                        default=self.entry.options.get(
                            CONF_BASE_URL, self.entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)
                        ),
                    ): str,
                }
            ),
        )

