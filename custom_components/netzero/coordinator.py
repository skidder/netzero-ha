"""Data coordinator for Netzero Energy."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from time import perf_counter
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import NetzeroApiAuthError, NetzeroApiClient, NetzeroApiError
from .const import DEFAULT_UPDATE_INTERVAL

LOGGER = logging.getLogger(__name__)


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _entry_to_kw(entry: dict[str, Any] | None) -> float | None:
    """Convert a value entry to kW."""
    if not entry:
        return None
    raw_val = _float_or_none(entry.get("raw_value"))
    if raw_val is not None:
        return raw_val / 1000
    val = _float_or_none(entry.get("value"))
    if val is not None:
        return val
    return None


def _entry_to_kwh(entry: dict[str, Any] | None) -> float | None:
    """Convert a value entry to kWh."""
    if not entry:
        return None
    raw_val = _float_or_none(entry.get("raw_value"))
    if raw_val is not None:
        return raw_val / 1000
    val = _float_or_none(entry.get("value"))
    if val is not None:
        return val
    return None


def _find_view(payload: dict[str, Any], title: str) -> dict[str, Any] | None:
    for view in payload.get("graph_views", []):
        if view.get("metadata", {}).get("title") == title:
            return view
    return None


def _latest_values(view: dict[str, Any]) -> tuple[dict[str, float], str | None]:
    data_points = (
        view.get("main_graph", {}).get("graph", {}).get("data_points", [])
    )
    if not data_points:
        return {}, None
    last_point = data_points[-1]
    values = {
        value.get("title"): _entry_to_kw(value)  # type: ignore[arg-type]
        for value in last_point.get("values", [])
    }
    timestamp = last_point.get("timestamp", {}).get("timestamp")
    return values, timestamp


class NetzeroDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch and parse Netzero data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: NetzeroApiClient,
        site_id: str,
        update_interval: timedelta | int | float = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        if isinstance(update_interval, (int, float)):
            update_interval = timedelta(seconds=update_interval)

        super().__init__(
            hass,
            logger=LOGGER,
            name="Netzero data",
            update_interval=update_interval,
        )
        self.api = api
        self.site_id = site_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API and reshape for sensors."""
        now = dt_util.as_local(dt_util.utcnow())
        start = dt_util.start_of_local_day(now)
        end = start + timedelta(days=1)
        time_zone = str(start.tzinfo) if start.tzinfo else "UTC"

        start_time = perf_counter()
        try:
            payload = await self.api.async_get_telemetry_history(time_zone, start, end)
        except NetzeroApiAuthError as err:
            raise UpdateFailed("Authentication failed") from err
        except NetzeroApiError as err:
            raise UpdateFailed(f"API error: {err}") from err
        finally:
            latency_ms = (perf_counter() - start_time) * 1000

        sensors: dict[str, float | None] = {}
        last_timestamp: str | None = None

        # Home view
        if (home_view := _find_view(payload, "Home")):
            sensors["home_total_used_kwh"] = _entry_to_kwh(home_view.get("main_value"))
            latest_values, last_timestamp = _latest_values(home_view)
            mapping = {
                "Used": "home_used_kw",
                "Used From Grid": "home_used_from_grid_kw",
                "Used From Solar": "home_used_from_solar_kw",
                "Used From Powerwall": "home_used_from_powerwall_kw",
            }
            for title, key in mapping.items():
                sensors[key] = latest_values.get(title)

        # Solar view
        if (solar_view := _find_view(payload, "Solar")):
            sensors["solar_total_generated_kwh"] = _entry_to_kwh(
                solar_view.get("main_value")
            )
            solar_values, ts = _latest_values(solar_view)
            if ts:
                last_timestamp = ts
            for title in ("Generated", "Solar"):
                if title in solar_values:
                    sensors["solar_generated_kw"] = solar_values[title]
                    break

        # Grid view
        if (grid_view := _find_view(payload, "Grid")):
            main_value = grid_view.get("main_value")
            if main_value:
                title = main_value.get("title", "").lower()
                if "import" in title:
                    sensors["grid_imported_kwh"] = _entry_to_kwh(main_value)
                if "export" in title:
                    sensors["grid_exported_kwh"] = _entry_to_kwh(main_value)
            secondary = grid_view.get("secondary_main_value")
            if secondary:
                title = secondary.get("title", "").lower()
                if "import" in title:
                    sensors["grid_imported_kwh"] = _entry_to_kwh(secondary)
                if "export" in title:
                    sensors["grid_exported_kwh"] = _entry_to_kwh(secondary)

        # Powerwall view
        if (pw_view := _find_view(payload, "Powerwall")):
            sensors["powerwall_discharged_kwh"] = _entry_to_kwh(
                pw_view.get("main_value")
            )
            sensors["powerwall_charged_kwh"] = _entry_to_kwh(
                pw_view.get("secondary_main_value")
            )
            pw_values, ts = _latest_values(pw_view)
            if ts:
                last_timestamp = ts
            if "Discharged" in pw_values:
                sensors["powerwall_discharge_kw"] = pw_values["Discharged"]
            if "Charged" in pw_values:
                sensors["powerwall_charge_kw"] = pw_values["Charged"]

        return {
            "sensors": sensors,
            "last_timestamp": last_timestamp,
            "latency_ms": latency_ms,
            "site_id": self.site_id,
            "timestamp": datetime.utcnow().isoformat(),
            "raw": payload,
        }

