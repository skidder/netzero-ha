# Netzero Energy Home Assistant Integration

Custom HACS integration to pull read-only solar and home energy data from the Netzero API.

## Features
- Read-only sensors for home usage, solar production, grid import/export, and Powerwall charge/discharge.
- DataUpdateCoordinator with 5-minute default polling.
- Diagnostics with redacted payloads.

## Install (HACS custom repo)
1. Add this repository as a custom integration in HACS.
2. Install the `Netzero Energy` integration.
3. Restart Home Assistant.

## Configure
1. Settings → Devices & Services → Add Integration → Netzero.
2. Enter:
   - Site ID
   - Bearer token (`Authorization` header)
   - X-Netzero-Token
   - Optional: X-User-Id, API base URL, Fleet base URL, App version
3. Default polling is 300 seconds; adjust in Options if desired.

## Tokens
Retrieve tokens from the Netzero web app network calls (as provided in the sample request). Tokens are stored securely by Home Assistant and only used for API reads.

## Sensors (initial set)
- Home: total used kWh, instantaneous power, power from grid/solar/powerwall.
- Solar: total generated kWh, instantaneous power.
- Grid: imported/exported kWh (if available).
- Powerwall: charged/discharged kWh, instantaneous charge/discharge power.

## Known limits
- No control/config writes; read-only telemetry.
- If tokens expire, update them in the integration options or re-create the entry.

