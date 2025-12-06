"""API client for Netzero Energy."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from aiohttp import ClientSession


class NetzeroApiError(Exception):
    """Base exception for Netzero API errors."""


class NetzeroApiAuthError(NetzeroApiError):
    """Raised when authentication fails."""


class NetzeroApiClient:
    """Simple async API client for Netzero."""

    def __init__(
        self,
        session: ClientSession,
        base_url: str,
        fleet_base_url: str,
        bearer_token: str,
        netzero_token: str,
        site_id: str,
        app_version: str,
        user_id: str | None = None,
    ) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._fleet_base_url = fleet_base_url.rstrip("/")
        self._bearer_token = bearer_token
        self._netzero_token = netzero_token
        self._user_id = user_id
        self._site_id = site_id
        self._app_version = app_version

    async def async_get_telemetry_history(
        self, time_zone: str, start: datetime, end: datetime
    ) -> dict[str, Any]:
        """Fetch daily telemetry graph for a site."""
        url = (
            f"{self._base_url}/api_proxy/api/1/energy_sites/"
            f"{self._site_id}/telemetry_history"
        )
        params = {
            "kind": "graph",
            "period": "day",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "language": "en",
            "client_time_zone": time_zone,
            "time_zone": time_zone,
        }
        headers = {
            "Authorization": f"Bearer {self._bearer_token}",
            "Content-Type": "application/json",
            "X-Netzero-Token": self._netzero_token,
            "X-Base-Url": self._fleet_base_url,
            "X-Site-Id": self._site_id,
            "X-Netzero-App-Version": self._app_version,
            "Origin": "https://app.netzero.energy",
            "Referer": "https://app.netzero.energy/",
        }
        if self._user_id:
            headers["X-User-Id"] = self._user_id

        async with self._session.get(url, headers=headers, params=params) as resp:
            if resp.status == 401:
                raise NetzeroApiAuthError("Authentication failed")
            if resp.status >= 400:
                raise NetzeroApiError(f"API error {resp.status}")
            data = await resp.json()

        # The API nests payloads under "response".
        if isinstance(data, dict) and "response" in data:
            return data["response"]
        return data

