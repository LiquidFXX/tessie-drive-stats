# Tessie Drive Stats for Home Assistant

A HACS-ready Home Assistant custom integration that reads drive and charging history directly from Tessie and exposes native Home Assistant sensors.

## Features

- UI setup; no REST YAML or `secrets.yaml` entry is required.
- Tessie token validation and VIN validation during setup.
- Automatic Home Assistant reauthentication flow if Tessie rejects/invalidates the token.
- Shared `DataUpdateCoordinator` so all entities use the same API data.
- Configurable refresh interval (1–60 minutes; default 5).
- Configurable first day of week (default Saturday).
- Uses Home Assistant's configured timezone for day/week/month/year boundaries.
- Uses Tessie's recorded charging-session `cost` field for cost totals.
- Diagnostics redact the Tessie access token and do not include coordinates or addresses.

## Sensors

For a vehicle named **Coaster**, Home Assistant will normally create entity IDs such as:

### Driving today

- `sensor.coaster_drives_today`
- `sensor.coaster_miles_today`
- `sensor.coaster_energy_today`
- `sensor.coaster_drive_time_today`
- `sensor.coaster_efficiency_today`
- `sensor.coaster_battery_used_today`

### Last drive

- `sensor.coaster_last_drive_miles`
- `sensor.coaster_last_drive_energy`
- `sensor.coaster_last_drive_time`
- `sensor.coaster_last_drive_efficiency`
- `sensor.coaster_last_drive_start`
- `sensor.coaster_last_drive_destination`
- `sensor.coaster_last_drive_starting_battery`
- `sensor.coaster_last_drive_ending_battery`
- `sensor.coaster_last_drive_battery_used`
- `sensor.coaster_last_drive_average_speed`
- `sensor.coaster_last_drive_max_speed`

### Charging cost

- `sensor.coaster_cost_today`
- `sensor.coaster_cost_this_week`
- `sensor.coaster_cost_this_month`
- `sensor.coaster_cost_this_year`

### Last charge

- `sensor.coaster_last_charge_cost`
- `sensor.coaster_last_charge_energy_added`
- `sensor.coaster_last_charge_location`

## Install manually for testing

1. Copy `custom_components/tessie_drive_stats` into your Home Assistant `/config/custom_components/` folder.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Search for **Tessie Drive Stats**.
5. Enter your Tessie access token and VIN.

You may paste either the raw Tessie token or `Bearer <token>`; the integration normalizes both forms.

## Install through HACS as a custom repository

HACS custom integrations must be hosted in a public GitHub repository.

1. Add this GitHub repository to HACS as a custom repository.
2. Open **HACS → Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Enter this repository URL and select **Integration**.
5. Install **Tessie Drive Stats**.
6. Restart Home Assistant.
7. Add the integration under **Settings → Devices & services**.

## Migrating from the REST YAML version

If you are already using the REST sensors, remove/comment out the Tessie drive-history and charge-history `rest:` entries before setting up this integration. Restart Home Assistant, then install this integration. This helps preserve clean entity IDs such as `sensor.coaster_miles_today` instead of getting `_2` suffixes.

The normal Tessie vehicle integration can remain installed. This integration uses the separate domain `tessie_drive_stats` and only adds historical/statistical sensors.

## Cost behavior

Cost totals are based on the `cost` value Tessie stores on each charging session. Sessions are assigned to a period based on their `started_at` timestamp. If Tessie reports a charge cost as `0`, this integration reports that session as zero cost; it does not invent an electricity rate.

The monetary unit shown by Home Assistant uses the currency configured in Home Assistant. The integration does not perform currency conversion.

## API usage

The coordinator normally makes two history requests per refresh:

- Today's completed drives: `GET /{vin}/drives`
- Year-to-date charging sessions: `GET /{vin}/charges`

If there are no drives today or no charges this year, it performs an additional small request to retrieve the latest historical record for the corresponding “Last …” sensors.

## Tessie API

Create an access token from Tessie Developer Settings. Tessie authentication uses an `Authorization: Bearer <token>` header.

## Version

0.1.0
