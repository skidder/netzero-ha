"""Home Assistant integration for Netzero Energy."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .api import NetzeroApiClient
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
    PLATFORMS,
)
from .coordinator import NetzeroDataUpdateCoordinator

type NetzeroConfigEntry = ConfigEntry


async def async_setup(hass: HomeAssistant, _config: dict) -> bool:
    """Set up via YAML is not supported; only config entries."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: NetzeroConfigEntry) -> bool:
    """Set up Netzero from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = aiohttp_client.async_get_clientsession(hass)
    data = entry.data
    options = entry.options

    base_url = options.get(CONF_BASE_URL, data.get(CONF_BASE_URL, DEFAULT_BASE_URL))
    fleet_base_url = options.get(
        CONF_FLEET_BASE_URL, data.get(CONF_FLEET_BASE_URL, DEFAULT_FLEET_BASE_URL)
    )
    app_version = options.get(
        CONF_APP_VERSION, data.get(CONF_APP_VERSION, DEFAULT_APP_VERSION)
    )
    update_interval = options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    if isinstance(update_interval, (int, float)):
        update_interval = timedelta(seconds=update_interval)

    api = NetzeroApiClient(
        session=session,
        base_url=base_url,
        fleet_base_url=fleet_base_url,
        bearer_token=data[CONF_BEARER_TOKEN],
        netzero_token=data[CONF_NETZERO_TOKEN],
        user_id=data.get(CONF_USER_ID),
        site_id=data[CONF_SITE_ID],
        app_version=app_version,
    )

    coordinator = NetzeroDataUpdateCoordinator(
        hass=hass,
        api=api,
        site_id=data[CONF_SITE_ID],
        update_interval=update_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NetzeroConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

