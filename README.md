# Tessie Drive Stats for Home Assistant

A HACS-ready Home Assistant custom integration for Tesla analytics backed by Tessie. It turns Tessie drive, charging, idle, consumption, battery, tire, navigation, software, historical-state, and optional fleet-invoice data into native Home Assistant entities.

Tessie Drive Stats is intended to complement the normal Tessie/Home Assistant vehicle integration. It focuses on history, totals, derived analytics, and diagnostic data rather than vehicle controls.

## Highlights

- UI setup; no REST YAML or `secrets.yaml` entry is required.
- Works with any Tesla available to the supplied Tessie access token.
- Supports multiple vehicles by adding one integration entry per VIN.
- Automatically fetches the vehicle name from Tessie during setup.
- Uses the Tessie vehicle name for Home Assistant device/entity naming while retaining the VIN as the permanent internal identifier.
- Configurable refresh interval (1–60 minutes; default 5).
- Configurable first day of week.
- Uses Home Assistant's configured timezone for day/week/month/year boundaries.
- Preserves existing VIN-based unique IDs when upgrading from earlier beta versions.
- Adds more than 200 sensor definitions plus tire-pressure warning binary sensors.
- Niche, recorder-heavy, best-effort, and fleet-only entities are disabled by default where appropriate.
- Diagnostics redact the Tessie access token and intentionally omit addresses, coordinates, and driving-path points.

## Analytics included

Tessie Drive Stats includes driving totals, AP/FSD distance, charging and Supercharger costs, idle/vampire-drain analytics, consumption since charge, battery telemetry and health trends, tire pressure, navigation, software information, firmware alerts, observed sleep/activity estimates, and optional fleet Supercharger invoice data.

Tessie exposes one drive-history field named `autopilot_distance`. It does not distinguish legacy Autopilot from FSD, so the integration deliberately reports **combined AP/FSD distance** rather than inventing a split Tessie does not provide.

## Vehicle naming

The setup form asks for a Tessie access token and VIN. The integration resolves the vehicle's Tessie display name automatically. Home Assistant uses that name for the device and new entity IDs, while the VIN remains the stable unique ID/device identifier.

For example, a vehicle Tessie names **My Tesla** may receive entity IDs beginning with:

```text
sensor.my_tesla_...
binary_sensor.my_tesla_...
```

Home Assistant preserves entity IDs that were already registered, so renaming a vehicle does not necessarily rename existing entity IDs. Depending on how Home Assistant names the device in your installation, your prefix may also look like `sensor.car_my_tesla_...`.

## Example entity IDs and values

The table below is the complete v0.3.0 entity catalog using a fictional vehicle named **My Tesla**.

**All values are illustrative examples only.** Actual states depend on the vehicle, Tessie data availability, Home Assistant unit settings, and account type. An unavailable Tessie field may appear as `unknown` or `unavailable` instead of the example shown.

Entities marked **Disabled** are disabled by default and can be enabled from **Settings → Devices & services → Tessie Drive Stats → your vehicle → Entities**.

### Driving and last drive

| Entity ID | Example value | Default |
|---|---:|---|
| `sensor.my_tesla_drives_today` | `2` | Enabled |
| `sensor.my_tesla_miles_today` | `23.11 mi` | Enabled |
| `sensor.my_tesla_energy_today` | `4.94 kWh` | Enabled |
| `sensor.my_tesla_drive_time_today` | `44.6 min` | Enabled |
| `sensor.my_tesla_efficiency_today` | `214 Wh/mi` | Enabled |
| `sensor.my_tesla_battery_used_today` | `8 %` | Enabled |
| `sensor.my_tesla_autopilot_fsd_miles_today` | `8.25 mi` | Enabled |
| `sensor.my_tesla_average_speed_today` | `35.8 mph` | Enabled |
| `sensor.my_tesla_max_speed_today` | `79 mph` | Enabled |
| `sensor.my_tesla_longest_drive_today` | `11.64 mi` | Enabled |
| `sensor.my_tesla_rated_range_used_today` | `23.27 mi` | Disabled |
| `sensor.my_tesla_average_inside_temperature_today` | `72.4 °F` | Disabled |
| `sensor.my_tesla_average_outside_temperature_today` | `88.1 °F` | Disabled |
| `sensor.my_tesla_drives_this_week` | `11` | Enabled |
| `sensor.my_tesla_miles_this_week` | `144.82 mi` | Enabled |
| `sensor.my_tesla_energy_this_week` | `31.12 kWh` | Enabled |
| `sensor.my_tesla_drive_time_this_week` | `280.5 min` | Enabled |
| `sensor.my_tesla_efficiency_this_week` | `215 Wh/mi` | Enabled |
| `sensor.my_tesla_autopilot_fsd_miles_this_week` | `94.30 mi` | Enabled |
| `sensor.my_tesla_average_speed_this_week` | `37.2 mph` | Enabled |
| `sensor.my_tesla_max_speed_this_week` | `81 mph` | Enabled |
| `sensor.my_tesla_longest_drive_this_week` | `26.44 mi` | Enabled |
| `sensor.my_tesla_rated_range_used_this_week` | `151.70 mi` | Disabled |
| `sensor.my_tesla_average_inside_temperature_this_week` | `72.0 °F` | Disabled |
| `sensor.my_tesla_average_outside_temperature_this_week` | `86.4 °F` | Disabled |
| `sensor.my_tesla_drives_this_month` | `46` | Enabled |
| `sensor.my_tesla_miles_this_month` | `612.40 mi` | Enabled |
| `sensor.my_tesla_energy_this_month` | `132.18 kWh` | Enabled |
| `sensor.my_tesla_drive_time_this_month` | `1178.3 min` | Enabled |
| `sensor.my_tesla_efficiency_this_month` | `216 Wh/mi` | Enabled |
| `sensor.my_tesla_autopilot_fsd_miles_this_month` | `456.20 mi` | Enabled |
| `sensor.my_tesla_average_speed_this_month` | `38.1 mph` | Enabled |
| `sensor.my_tesla_max_speed_this_month` | `84 mph` | Enabled |
| `sensor.my_tesla_longest_drive_this_month` | `118.72 mi` | Enabled |
| `sensor.my_tesla_rated_range_used_this_month` | `641.30 mi` | Disabled |
| `sensor.my_tesla_average_inside_temperature_this_month` | `71.8 °F` | Disabled |
| `sensor.my_tesla_average_outside_temperature_this_month` | `85.2 °F` | Disabled |
| `sensor.my_tesla_drives_this_year` | `318` | Enabled |
| `sensor.my_tesla_miles_this_year` | `4156.08 mi` | Enabled |
| `sensor.my_tesla_energy_this_year` | `901.72 kWh` | Enabled |
| `sensor.my_tesla_drive_time_this_year` | `8120.5 min` | Enabled |
| `sensor.my_tesla_efficiency_this_year` | `217 Wh/mi` | Enabled |
| `sensor.my_tesla_autopilot_fsd_miles_this_year` | `2984.60 mi` | Enabled |
| `sensor.my_tesla_average_speed_this_year` | `38.7 mph` | Enabled |
| `sensor.my_tesla_max_speed_this_year` | `87 mph` | Enabled |
| `sensor.my_tesla_longest_drive_this_year` | `247.38 mi` | Enabled |
| `sensor.my_tesla_rated_range_used_this_year` | `4342.10 mi` | Disabled |
| `sensor.my_tesla_average_inside_temperature_this_year` | `71.6 °F` | Disabled |
| `sensor.my_tesla_average_outside_temperature_this_year` | `74.3 °F` | Disabled |
| `sensor.my_tesla_last_drive_miles` | `11.64 mi` | Enabled |
| `sensor.my_tesla_last_drive_autopilot_fsd_miles` | `8.25 mi` | Enabled |
| `sensor.my_tesla_last_drive_energy` | `2.44 kWh` | Enabled |
| `sensor.my_tesla_last_drive_time` | `23.5 min` | Enabled |
| `sensor.my_tesla_last_drive_efficiency` | `210 Wh/mi` | Enabled |
| `sensor.my_tesla_last_drive_start` | `Work` | Enabled |
| `sensor.my_tesla_last_drive_destination` | `Home` | Enabled |
| `sensor.my_tesla_last_drive_starting_battery` | `65 %` | Enabled |
| `sensor.my_tesla_last_drive_ending_battery` | `61 %` | Enabled |
| `sensor.my_tesla_last_drive_battery_used` | `4 %` | Enabled |
| `sensor.my_tesla_last_drive_average_speed` | `35 mph` | Enabled |
| `sensor.my_tesla_last_drive_max_speed` | `79 mph` | Enabled |
| `sensor.my_tesla_last_drive_inside_temperature` | `72.0 °F` | Enabled |
| `sensor.my_tesla_last_drive_outside_temperature` | `87.0 °F` | Enabled |
| `sensor.my_tesla_last_drive_rated_range_used` | `11.45 mi` | Enabled |
| `sensor.my_tesla_last_drive_tag` | `Commute` | Enabled |
| `sensor.my_tesla_last_drive_path_points` | `186` | Disabled |
| `sensor.my_tesla_last_drive_path_autopilot_share` | `71.4 %` | Disabled |

### Charging, Supercharging, and idle

| Entity ID | Example value | Default |
|---|---:|---|
| `sensor.my_tesla_cost_today` | `$1.84` | Enabled |
| `sensor.my_tesla_supercharger_sessions_today` | `0` | Enabled |
| `sensor.my_tesla_supercharger_energy_today` | `0.00 kWh` | Enabled |
| `sensor.my_tesla_supercharger_cost_today` | `$0.00` | Enabled |
| `sensor.my_tesla_cost_this_week` | `$8.62` | Enabled |
| `sensor.my_tesla_supercharger_sessions_this_week` | `1` | Enabled |
| `sensor.my_tesla_supercharger_energy_this_week` | `42.60 kWh` | Enabled |
| `sensor.my_tesla_supercharger_cost_this_week` | `$15.34` | Enabled |
| `sensor.my_tesla_cost_this_month` | `$31.48` | Enabled |
| `sensor.my_tesla_supercharger_sessions_this_month` | `3` | Enabled |
| `sensor.my_tesla_supercharger_energy_this_month` | `118.40 kWh` | Enabled |
| `sensor.my_tesla_supercharger_cost_this_month` | `$42.65` | Enabled |
| `sensor.my_tesla_cost_this_year` | `$284.76` | Enabled |
| `sensor.my_tesla_supercharger_sessions_this_year` | `18` | Enabled |
| `sensor.my_tesla_supercharger_energy_this_year` | `742.80 kWh` | Enabled |
| `sensor.my_tesla_supercharger_cost_this_year` | `$267.41` | Enabled |
| `sensor.my_tesla_last_charge_cost` | `$1.84` | Enabled |
| `sensor.my_tesla_last_charge_energy_added` | `18.60 kWh` | Enabled |
| `sensor.my_tesla_last_charge_location` | `Home` | Enabled |
| `sensor.my_tesla_last_supercharger_cost` | `$15.34` | Enabled |
| `sensor.my_tesla_last_supercharger_energy_added` | `42.60 kWh` | Enabled |
| `sensor.my_tesla_last_supercharger_location` | `Summerville Supercharger` | Enabled |
| `sensor.my_tesla_idle_sessions_today` | `4` | Enabled |
| `sensor.my_tesla_idle_time_today` | `382.5 min` | Enabled |
| `sensor.my_tesla_idle_energy_today` | `1.42 kWh` | Enabled |
| `sensor.my_tesla_idle_battery_used_today` | `2.0 %` | Enabled |
| `sensor.my_tesla_idle_rated_range_used_today` | `5.80 mi` | Enabled |
| `sensor.my_tesla_idle_sentry_time_today` | `211.4 min` | Enabled |
| `sensor.my_tesla_idle_climate_time_today` | `42.7 min` | Enabled |
| `sensor.my_tesla_idle_sessions_this_week` | `21` | Enabled |
| `sensor.my_tesla_idle_time_this_week` | `1884.2 min` | Enabled |
| `sensor.my_tesla_idle_energy_this_week` | `7.88 kWh` | Enabled |
| `sensor.my_tesla_idle_battery_used_this_week` | `11.0 %` | Enabled |
| `sensor.my_tesla_idle_rated_range_used_this_week` | `31.40 mi` | Enabled |
| `sensor.my_tesla_idle_sentry_time_this_week` | `988.1 min` | Enabled |
| `sensor.my_tesla_idle_climate_time_this_week` | `184.0 min` | Enabled |
| `sensor.my_tesla_idle_sessions_this_month` | `86` | Enabled |
| `sensor.my_tesla_idle_time_this_month` | `7482.0 min` | Enabled |
| `sensor.my_tesla_idle_energy_this_month` | `31.45 kWh` | Enabled |
| `sensor.my_tesla_idle_battery_used_this_month` | `43.0 %` | Enabled |
| `sensor.my_tesla_idle_rated_range_used_this_month` | `126.80 mi` | Enabled |
| `sensor.my_tesla_idle_sentry_time_this_month` | `3840.5 min` | Enabled |
| `sensor.my_tesla_idle_climate_time_this_month` | `712.8 min` | Enabled |
| `sensor.my_tesla_idle_sessions_this_year` | `591` | Enabled |
| `sensor.my_tesla_idle_time_this_year` | `52644.7 min` | Enabled |
| `sensor.my_tesla_idle_energy_this_year` | `219.74 kWh` | Enabled |
| `sensor.my_tesla_idle_battery_used_this_year` | `301.0 %` | Enabled |
| `sensor.my_tesla_idle_rated_range_used_this_year` | `892.30 mi` | Enabled |
| `sensor.my_tesla_idle_sentry_time_this_year` | `27120.4 min` | Enabled |
| `sensor.my_tesla_idle_climate_time_this_year` | `5182.6 min` | Enabled |
| `sensor.my_tesla_last_idle_time` | `96.5 min` | Enabled |
| `sensor.my_tesla_last_idle_energy` | `0.38 kWh` | Enabled |
| `sensor.my_tesla_last_idle_battery_used` | `1.0 %` | Enabled |
| `sensor.my_tesla_last_idle_rated_range_used` | `2.10 mi` | Enabled |
| `sensor.my_tesla_last_idle_sentry_share` | `78.0 %` | Enabled |
| `sensor.my_tesla_last_idle_climate_share` | `8.0 %` | Enabled |
| `sensor.my_tesla_last_idle_location` | `Home` | Enabled |
| `sensor.my_tesla_last_idle_starting_battery` | `62 %` | Enabled |
| `sensor.my_tesla_last_idle_ending_battery` | `61 %` | Enabled |
| `sensor.my_tesla_last_idle_state_battery_level` | `61 %` | Disabled |
| `sensor.my_tesla_last_idle_state_range` | `168.4 mi` | Disabled |

### Consumption and battery

| Entity ID | Example value | Default |
|---|---:|---|
| `sensor.my_tesla_consumption_last_charge_at` | `2026-08-15 21:42:18` | Enabled |
| `sensor.my_tesla_distance_since_charge` | `42.80 mi` | Enabled |
| `sensor.my_tesla_battery_used_since_charge` | `18.0 %` | Enabled |
| `sensor.my_tesla_battery_used_by_driving_since_charge` | `13.0 %` | Enabled |
| `sensor.my_tesla_battery_used_non_driving_since_charge` | `5.0 %` | Enabled |
| `sensor.my_tesla_rated_range_used_since_charge` | `48.60 mi` | Enabled |
| `sensor.my_tesla_rated_range_used_by_driving_since_charge` | `41.20 mi` | Enabled |
| `sensor.my_tesla_ideal_range_used_since_charge` | `45.10 mi` | Disabled |
| `sensor.my_tesla_ideal_range_used_by_driving_since_charge` | `39.80 mi` | Disabled |
| `sensor.my_tesla_energy_used_since_charge` | `10.82 kWh` | Enabled |
| `sensor.my_tesla_energy_used_by_driving_since_charge` | `8.26 kWh` | Enabled |
| `sensor.my_tesla_energy_used_non_driving_since_charge` | `2.56 kWh` | Enabled |
| `sensor.my_tesla_driving_energy_share_since_charge` | `76.3 %` | Enabled |
| `sensor.my_tesla_battery_level_current` | `61 %` | Enabled |
| `sensor.my_tesla_battery_range_current` | `168.4 mi` | Enabled |
| `sensor.my_tesla_ideal_battery_range_current` | `176.8 mi` | Enabled |
| `sensor.my_tesla_phantom_drain` | `1.2 %` | Enabled |
| `sensor.my_tesla_energy_remaining` | `48.70 kWh` | Enabled |
| `sensor.my_tesla_lifetime_energy_used` | `12845.6 kWh` | Enabled |
| `sensor.my_tesla_pack_current` | `-4.2 A` | Disabled |
| `sensor.my_tesla_pack_voltage` | `386.7 V` | Disabled |
| `sensor.my_tesla_battery_module_temp_min` | `29.4 °C` | Enabled |
| `sensor.my_tesla_battery_module_temp_max` | `31.1 °C` | Enabled |
| `sensor.my_tesla_battery_module_temp_spread` | `1.7 °C` | Enabled |
| `sensor.my_tesla_battery_health` | `91.4 %` | Enabled |
| `sensor.my_tesla_battery_degradation` | `8.6 %` | Enabled |
| `sensor.my_tesla_battery_capacity` | `72.66 kWh` | Enabled |
| `sensor.my_tesla_battery_original_capacity` | `79.50 kWh` | Enabled |
| `sensor.my_tesla_battery_max_range` | `298.4 mi` | Enabled |
| `sensor.my_tesla_battery_max_ideal_range` | `312.7 mi` | Enabled |
| `sensor.my_tesla_battery_health_measurements_this_year` | `41` | Enabled |
| `sensor.my_tesla_battery_capacity_change_30_days` | `-0.22 kWh` | Enabled |
| `sensor.my_tesla_battery_capacity_change_this_year` | `-1.18 kWh` | Enabled |
| `sensor.my_tesla_battery_max_range_change_30_days` | `-0.8 mi` | Enabled |
| `sensor.my_tesla_battery_max_range_change_this_year` | `-4.6 mi` | Enabled |

### Vehicle, tires, software, activity, and fleet

| Entity ID | Example value | Default |
|---|---:|---|
| `sensor.my_tesla_vehicle_status` | `asleep` | Enabled |
| `sensor.my_tesla_odometer_current` | `81485.3 mi` | Enabled |
| `sensor.my_tesla_software_version` | `2026.26.7` | Enabled |
| `sensor.my_tesla_software_update_status` | `available` | Enabled |
| `sensor.my_tesla_software_update_version` | `2026.32.1` | Enabled |
| `sensor.my_tesla_software_update_download` | `0 %` | Enabled |
| `sensor.my_tesla_software_update_install` | `0 %` | Enabled |
| `sensor.my_tesla_navigation_destination` | `Home` | Enabled |
| `sensor.my_tesla_navigation_miles_to_arrival` | `12.4 mi` | Enabled |
| `sensor.my_tesla_navigation_minutes_to_arrival` | `22.0 min` | Enabled |
| `sensor.my_tesla_navigation_traffic_delay` | `4.0 min` | Enabled |
| `sensor.my_tesla_navigation_energy_at_arrival` | `54 %` | Enabled |
| `sensor.my_tesla_charging_state_current` | `Disconnected` | Enabled |
| `sensor.my_tesla_charge_rate_current` | `0.0 mph` | Enabled |
| `sensor.my_tesla_charger_power_current` | `0.0 kW` | Enabled |
| `sensor.my_tesla_charge_limit` | `80 %` | Enabled |
| `sensor.my_tesla_time_to_full_charge` | `0.0 h` | Enabled |
| `sensor.my_tesla_inside_temperature_current` | `24.1 °C` | Enabled |
| `sensor.my_tesla_outside_temperature_current` | `31.7 °C` | Enabled |
| `sensor.my_tesla_connection_status` | `connected` | Enabled |
| `sensor.my_tesla_tire_pressure_front_left` | `42.1 psi` | Enabled |
| `sensor.my_tesla_tire_status_front_left` | `normal` | Disabled |
| `sensor.my_tesla_tire_pressure_front_right` | `41.8 psi` | Enabled |
| `sensor.my_tesla_tire_status_front_right` | `normal` | Disabled |
| `sensor.my_tesla_tire_pressure_rear_left` | `42.4 psi` | Enabled |
| `sensor.my_tesla_tire_status_rear_left` | `normal` | Disabled |
| `sensor.my_tesla_tire_pressure_rear_right` | `42.0 psi` | Enabled |
| `sensor.my_tesla_tire_status_rear_right` | `normal` | Disabled |
| `sensor.my_tesla_firmware_alert_count` | `1` | Enabled |
| `sensor.my_tesla_latest_firmware_alert` | `VCFRONT_a447` | Enabled |
| `sensor.my_tesla_latest_firmware_alert_at` | `2026-08-15 14:18:32` | Enabled |
| `sensor.my_tesla_observed_awake_time_today` | `96.4 min` | Disabled |
| `sensor.my_tesla_observed_asleep_time_today` | `524.7 min` | Disabled |
| `sensor.my_tesla_observed_waiting_for_sleep_time_today` | `18.2 min` | Disabled |
| `sensor.my_tesla_observed_wakeups_today` | `3` | Disabled |
| `sensor.my_tesla_charging_invoice_access` | `fleet_only` | Disabled |
| `sensor.my_tesla_supercharger_invoice_count_this_year` | `12` | Disabled |
| `sensor.my_tesla_supercharger_invoice_energy_this_year` | `518.40 kWh` | Disabled |
| `sensor.my_tesla_supercharger_invoice_charging_fees_this_year` | `$146.88` | Disabled |
| `sensor.my_tesla_supercharger_invoice_idle_fees_this_year` | `$0.00` | Disabled |
| `sensor.my_tesla_supercharger_invoice_total_cost_this_year` | `$146.88` | Disabled |
| `sensor.my_tesla_last_supercharger_invoice_cost` | `$18.24` | Disabled |
| `sensor.my_tesla_last_supercharger_invoice_cost_per_kwh` | `$0.360/kWh` | Disabled |

### Tire-pressure warning binary sensors

| Entity ID | Example value | Meaning |
|---|---:|---|
| `binary_sensor.my_tesla_tire_pressure_low_front_left` | `off` | Pressure not reported low |
| `binary_sensor.my_tesla_tire_pressure_low_front_right` | `off` | Pressure not reported low |
| `binary_sensor.my_tesla_tire_pressure_low_rear_left` | `off` | Pressure not reported low |
| `binary_sensor.my_tesla_tire_pressure_low_rear_right` | `off` | Pressure not reported low |

That is the complete v0.3.0 catalog: **206 sensor entities plus 4 tire-pressure warning binary sensors**.

## Update cadence and API load

The configured refresh interval controls the core drive/charging refresh and current-state analytics. To avoid repeatedly requesting slow-changing or larger datasets, other data is cached separately:

- Core drive/charge/current-state data: configured refresh interval (default 5 minutes)
- Historical idles and firmware alerts: about every 1 hour
- Historical state/activity samples: about every 30 minutes
- Battery health, battery-health history, and fleet invoices: about every 6 hours
- Last-drive route: fetched when the latest drive changes

An optional endpoint failure is isolated from the core drive/charging coordinator when possible, so a temporary battery-health, history, path, firmware, or fleet-only endpoint problem should not make the main drive sensors unavailable. Authentication failures still trigger Home Assistant's reauthentication flow.

## Recorder considerations

The optional last-drive route entity can expose GPS path points as attributes. It is disabled by default and limits the stored route to at most 200 points to reduce Home Assistant recorder/database growth.

## Install through HACS as a custom repository

1. Open **HACS → Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/LiquidFXX/tessie-drive-stats` and select **Integration**.
4. Install **Tessie Drive Stats**.
5. Restart Home Assistant.
6. Open **Settings → Devices & services → Add integration**.
7. Search for **Tessie Drive Stats** and enter the Tessie access token and vehicle VIN.

To add another vehicle, add Tessie Drive Stats again with that vehicle's VIN.

You may paste either the raw Tessie token or `Bearer <token>`; the integration normalizes both forms.

## Updating from an earlier beta

Version 0.3.0 preserves the existing VIN-based unique IDs for earlier sensors and adds the new analytics as additional entities. After updating through HACS, restart Home Assistant so the new `sensor` and `binary_sensor` platforms/entities are registered.

Some diagnostic, route, observed-activity, tire-status, and fleet-invoice entities are disabled by default. Enable any of them from the vehicle's entity list if you want to use them.

## Migrating from REST YAML sensors

If you already have manually-created Tessie REST sensors, remove or rename conflicting sensors before configuring this integration if you want to avoid Home Assistant assigning `_2` suffixes to duplicate entity IDs.

The normal Tessie vehicle integration can remain installed. Tessie Drive Stats uses the separate `tessie_drive_stats` domain.

## Privacy

The integration stores the Tessie access token in the Home Assistant config entry as required for API access. Diagnostics redact the token and avoid returning street addresses, GPS coordinates, or route points.

Normal Home Assistant entity states may still contain user-requested data such as last-drive locations or navigation destinations. Treat downloaded diagnostics and screenshots according to your own privacy requirements.

## Tessie API

Create an access token from Tessie Developer Settings. Tessie authentication uses an `Authorization: Bearer <token>` header.

### New to Tessie?

If you're signing up for Tessie and would like to support this project, you can use my referral link:

**[Sign up for Tessie with my referral link](https://share.tessie.com/8TNHZg25Zwb)**

*Disclosure: This is a personal Tessie referral link.*

## Development validation

The repository includes synthetic calculation tests. No real VIN, trip address, or access token is included in the test fixtures.

## Version

0.3.0
