# Tessie Drive Stats for Home Assistant

A HACS-ready Home Assistant custom integration that reads Tesla drive and charging history directly from Tessie and exposes native Home Assistant sensors.

## Features

- UI setup; no REST YAML or `secrets.yaml` entry is required.
- Works with any Tesla available to the supplied Tessie access token.
- Supports multiple vehicles by adding one integration entry per VIN.
- Automatically fetches the vehicle name from Tessie during setup.
- Uses the Tessie vehicle name for the Home Assistant device and entity names.
- Uses the VIN as the permanent internal unique identifier, so the identity stays stable even if the vehicle name changes.
- Falls back to `Tesla <last 6 VIN digits>` only if Tessie does not provide a vehicle name.
- Tessie token validation and VIN validation during setup.
- Automatic Home Assistant reauthentication flow if Tessie rejects or invalidates the token.
- Shared `DataUpdateCoordinator` so all entities use the same API data.
- Configurable refresh interval (1–60 minutes; default 5).
- Configurable first day of week (default Monday).
- Uses Home Assistant's configured timezone for day/week/month/year boundaries.
- Uses Tessie's recorded charging-session `cost` field for cost totals.
- Diagnostics redact the Tessie access token and do not include coordinates or addresses.

## Vehicle naming

The setup form only asks for a Tessie access token and VIN. The integration then resolves the vehicle name from Tessie automatically.

For example, if Tessie reports a vehicle name of **My Tesla**, Home Assistant will create a device named **My Tesla** and new entities will normally receive IDs such as:

- `sensor.my_tesla_drives_today`
- `sensor.my_tesla_miles_today`
- `sensor.my_tesla_energy_today`
- `sensor.my_tesla_cost_today`
- `sensor.my_tesla_cost_this_week`
- `sensor.my_tesla_last_drive_miles`

The exact entity IDs can vary if entities with the same IDs already exist in Home Assistant. The VIN is used only for stable internal unique IDs and device identity; it is not normally exposed in the entity IDs.

## Sensors

### Driving today

- Drives today
- Miles today
- Energy today
- Drive time today
- Efficiency today
- Battery used today

### Last drive

- Last drive miles
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

### Charging cost

- Cost today
- Cost this week
- Cost this month
- Cost this year

### Last charge

- Last charge cost
- Last charge energy added
- Last charge location

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

## Existing installations and vehicle names

Version 0.1.2 migrates older config entries by fetching the Tessie vehicle name and updating the Home Assistant device/config-entry name. Home Assistant preserves existing entity IDs in its entity registry, so entities that were already created under an older fallback name may retain those old entity IDs. Freshly created entities use the Tessie vehicle name automatically.

## Cost behavior

Cost totals are based on the `cost` value Tessie stores on each charging session. Sessions are assigned to a period based on their `started_at` timestamp. If Tessie reports a charge cost as `0`, this integration reports that session as zero cost; it does not invent an electricity rate.

The monetary unit shown by Home Assistant uses the currency configured in Home Assistant. The integration does not perform currency conversion.

## API usage

The coordinator normally makes two history requests per refresh:

- Today's completed drives: `GET /{vin}/drives`
- Year-to-date charging sessions: `GET /{vin}/charges`

If there are no drives today or no charges this year, it performs an additional small request to retrieve the latest historical record for the corresponding “Last …” sensors.

During setup or migration, the integration also reads Tessie's vehicle metadata to resolve the vehicle name.

## Tessie API

Create an access token from Tessie Developer Settings. Tessie authentication uses an `Authorization: Bearer <token>` header.

## Version

0.1.2
