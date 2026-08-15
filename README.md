# Tessie Drive Stats for Home Assistant

A HACS-ready Home Assistant custom integration that reads Tesla drive, charging, Supercharger, and battery-health history directly from Tessie and exposes native Home Assistant sensors.

## Features

- UI setup; no REST YAML or `secrets.yaml` entry is required.
- Works with any Tesla available to the supplied Tessie access token.
- Supports multiple vehicles by adding one integration entry per VIN.
- Automatically fetches the vehicle name from Tessie during setup.
- Uses the Tessie vehicle name for the Home Assistant device and entity names.
- Uses the VIN as the permanent internal unique identifier.
- Configurable refresh interval (1–60 minutes; default 5).
- Configurable first day of week (default Monday).
- Uses Home Assistant's configured timezone for day/week/month/year boundaries.
- Uses Tessie's recorded charging-session `cost` field for cost totals.
- Tracks combined Autopilot/FSD miles from Tessie's `autopilot_distance` drive field.
- Tracks Supercharger sessions, energy, and cost from Tessie's `is_supercharger` field.
- Pulls Tessie's battery-health summary: health, degradation, capacity, original capacity, and max range.
- Battery health is refreshed every 6 hours because it changes slowly.
- Diagnostics redact the Tessie access token and do not include coordinates or addresses.

## Vehicle naming

The setup form asks for a Tessie access token and VIN. The integration resolves the vehicle name from Tessie automatically. Home Assistant uses that vehicle name for the device and new entity IDs, while the VIN remains the stable internal unique identifier.

For example, if Tessie reports **My Tesla**, Home Assistant may create entity IDs beginning with `sensor.my_tesla_...`.

## Sensors

### Driving today

- Drives today
- Miles today
- Energy today
- Drive time today
- Efficiency today
- Battery used today

### Autopilot / FSD distance

Tessie exposes one historical drive field named `autopilot_distance`. It does not distinguish legacy Autopilot from FSD, so this integration reports **combined AP/FSD miles**.

- AP/FSD miles today
- AP/FSD miles this week
- AP/FSD miles this month
- AP/FSD miles this year
- Last drive AP/FSD miles

If Tessie returns `null` for `autopilot_distance` on drives, the corresponding AP/FSD sensor may be unavailable rather than incorrectly reporting zero.

### Last drive

- Last drive miles
- Last drive AP/FSD miles
- Last drive energy
- Last drive time
- Last drive efficiency
- Last drive start
- Last drive destination
- Last drive starting battery
- Last drive ending battery
- Last drive battery used
- Last drive average speed
- Last drive max speed

### All charging cost

- Cost today
- Cost this week
- Cost this month
- Cost this year

### Supercharger statistics

- Supercharger sessions today
- Supercharger sessions this week
- Supercharger sessions this month
- Supercharger sessions this year
- Supercharger energy today
- Supercharger energy this week
- Supercharger energy this month
- Supercharger energy this year
- Supercharger cost today
- Supercharger cost this week
- Supercharger cost this month
- Supercharger cost this year

### Last charge / Supercharger

- Last charge cost
- Last charge energy added
- Last charge location
- Last Supercharger cost
- Last Supercharger energy added
- Last Supercharger location

### Battery health

- Battery health (%)
- Battery degradation (%)
- Battery capacity (kWh)
- Original battery capacity (kWh)
- Battery max range (mi)

## Install manually for testing

1. Copy `custom_components/tessie_drive_stats` into your Home Assistant `/config/custom_components/` folder.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Search for **Tessie Drive Stats**.
5. Enter your Tessie access token and the VIN of the vehicle you want to monitor.
6. The vehicle name is fetched automatically from Tessie.

You may paste either the raw Tessie token or `Bearer <token>`; the integration normalizes both forms.

To monitor another vehicle, add Tessie Drive Stats again with that vehicle's VIN.

## Install through HACS as a custom repository

1. Open **HACS → Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Enter this repository URL and select **Integration**.
4. Install **Tessie Drive Stats**.
5. Restart Home Assistant.
6. Add the integration under **Settings → Devices & services**.

## Migrating from REST YAML sensors

If you already have Tessie drive-history or charge-history REST sensors, remove or rename those sensors before setting up this integration if you want to avoid Home Assistant assigning `_2` suffixes to overlapping entity IDs.

The normal Tessie vehicle integration can remain installed. Tessie Drive Stats uses the separate domain `tessie_drive_stats` and adds historical/statistical sensors only.

## Cost behavior

Cost totals are based on the `cost` value Tessie stores on each charging session. If Tessie reports a session cost as `0`, this integration reports zero; it does not invent an electricity rate.

Supercharger statistics are identified from Tessie's `is_supercharger` field.

The monetary unit shown by Home Assistant uses the currency configured in Home Assistant. The integration does not perform currency conversion.

## API usage

The coordinator normally requests:

- Year-to-date completed drives: `GET /{vin}/drives`
- Year-to-date charging sessions: `GET /{vin}/charges`
- Battery health: `GET /battery_health` every 6 hours

If there are no drives or charges in the current year, it may perform a small additional request to retrieve the latest historical drive, charge, or Supercharger for the corresponding “Last …” sensors.

During setup or migration, the integration also reads Tessie's vehicle metadata to resolve the vehicle name.

## Tessie API

Create an access token from Tessie Developer Settings. Tessie authentication uses an `Authorization: Bearer <token>` header.

## Version

0.2.0
