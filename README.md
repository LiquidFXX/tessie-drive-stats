# Tessie Drive Stats for Home Assistant

A HACS-ready Home Assistant custom integration for Tesla analytics backed by Tessie. It turns Tessie drive, charging, idle, consumption, battery, tire, navigation, software, lifetime-history, and optional fleet-invoice data into native Home Assistant entities.

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
- Adds **247 sensor definitions plus 4 tire-pressure warning binary sensors**.
- Includes persistent lifetime driving, charging, Supercharging, idle/vampire-drain, and battery-health history analytics.
- Niche, recorder-heavy, best-effort, and fleet-only entities are disabled by default where appropriate.
- Diagnostics redact the Tessie access token and intentionally omit addresses, coordinates, and driving-path points.
- The persistent lifetime cache is privacy-minimized and does not store historical street addresses or GPS coordinates.

## Analytics included

Tessie Drive Stats includes driving totals, AP/FSD distance, charging and Supercharger costs, idle/vampire-drain analytics, consumption since charge, battery telemetry and health trends, tire pressure, navigation, software information, firmware alerts, observed sleep/activity estimates, lifetime history, and optional fleet Supercharger invoice data.

Tessie exposes one drive-history field named `autopilot_distance`. It does not distinguish legacy Autopilot from FSD, so the integration deliberately reports **combined AP/FSD distance** rather than inventing a split Tessie does not provide.

## Lifetime analytics

Version 0.4.0 distinguishes two types of lifetime data:

- **Vehicle lifetime** — counters Tessie reports directly from the vehicle, such as odometer and `lifetime_energy_used`.
- **Tessie recorded lifetime** — totals calculated from all drive, charge, idle, and battery-health history available in Tessie.

Recorded-lifetime values are intentionally labeled **Recorded lifetime** because Tessie may have started collecting data after the vehicle was purchased. Coverage sensors such as `recorded_lifetime_data_since`, `recorded_lifetime_driving_since`, and `battery_history_since` show how far back the available Tessie history actually goes.

On the first v0.4.0 refresh, the integration performs a one-time historical backfill. It stores only the fields required for lifetime calculations in Home Assistant storage. After that it refreshes lifetime history about every 6 hours using a short overlap window, with a full reconciliation about every 30 days to pick up edited historical values such as charging costs.

## Dashboard & card examples

Want to see what Tessie Drive Stats can look like in Home Assistant?

**[View the Tesla-inspired dashboard and card examples →](examples/README.md)**

The examples gallery includes screenshots for vehicle status, charging, driving periods, Last Drive, battery health, idle/vampire drain, charging costs, Supercharging, tire pressure, navigation, and software/alerts. Version 0.4.0 also includes a reusable **[Tesla-style Lifetime card YAML](examples/lifetime-card.yaml)** with a configurable vehicle entity prefix.

<p align="center">
  <a href="examples/README.md">
    <img src="examples/screenshots/battery.png" alt="Battery analytics card example" width="360">
  </a>
</p>

<p align="center"><sub>Battery analytics example — click the card to view the full gallery.</sub></p>

## Vehicle naming

The setup form asks for a Tessie access token and VIN. The integration resolves the vehicle's Tessie display name automatically. Home Assistant uses that name for the device and new entity IDs, while the VIN remains the stable unique ID/device identifier.

For example, a vehicle Tessie names **My Tesla** may receive entity IDs beginning with:

```text
sensor.my_tesla_...
binary_sensor.my_tesla_...
```

Home Assistant preserves entity IDs that were already registered, so renaming a vehicle does not necessarily rename existing entity IDs. Depending on how Home Assistant names the device in your installation, your prefix may also look like `sensor.car_my_tesla_...`.

## Example entity IDs and values

The table below is the complete v0.4.0 entity catalog using a fictional vehicle named **My Tesla**.

**All values are illustrative examples only.** Actual states depend on the vehicle, Tessie data availability, Home Assistant unit settings, account type, and the date Tessie began recording the vehicle. An unavailable Tessie field may appear as `unknown` or `unavailable` instead of the example shown.

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

### Lifetime — vehicle and Tessie recorded history

`lifetime_odometer` and the existing `lifetime_energy_used` sensor are vehicle-lifetime counters. Sensors beginning with `recorded_lifetime_` summarize only the historical records available from Tessie.

| Entity ID | Example value | Default |
|---|---:|---|
| `sensor.my_tesla_lifetime_odometer` | `81485.3 mi` | Enabled |
| `sensor.my_tesla_recorded_lifetime_data_since` | `2024-01-03 08:14:00` | Enabled |
| `sensor.my_tesla_recorded_lifetime_driving_since` | `2024-01-03 08:14:00` | Enabled |
| `sensor.my_tesla_recorded_lifetime_charging_since` | `2024-01-03 21:36:00` | Enabled |
| `sensor.my_tesla_recorded_lifetime_idle_since` | `2024-01-03 09:02:00` | Enabled |
| `sensor.my_tesla_battery_history_since` | `2024-02-11 12:00:00` | Enabled |
| `sensor.my_tesla_recorded_lifetime_last_synced` | `2026-08-17 10:00:00` | Disabled |
| `sensor.my_tesla_recorded_lifetime_drives` | `1580` | Enabled |
| `sensor.my_tesla_recorded_lifetime_miles` | `18432.64 mi` | Enabled |
| `sensor.my_tesla_recorded_lifetime_drive_time` | `35124.7 min` | Enabled |
| `sensor.my_tesla_recorded_lifetime_drive_energy` | `4326.20 kWh` | Enabled |
| `sensor.my_tesla_recorded_lifetime_efficiency` | `235 Wh/mi` | Enabled |
| `sensor.my_tesla_recorded_lifetime_ap_fsd_miles` | `12746.30 mi` | Enabled |
| `sensor.my_tesla_recorded_lifetime_ap_fsd_share` | `69.2 %` | Enabled |
| `sensor.my_tesla_recorded_lifetime_average_speed` | `31.5 mph` | Enabled |
| `sensor.my_tesla_recorded_lifetime_max_speed` | `92 mph` | Enabled |
| `sensor.my_tesla_recorded_lifetime_longest_drive` | `247.38 mi` | Enabled |
| `sensor.my_tesla_recorded_lifetime_rated_range_used` | `19624.80 mi` | Enabled |
| `sensor.my_tesla_recorded_lifetime_average_inside_temperature` | `71.5 °F` | Enabled |
| `sensor.my_tesla_recorded_lifetime_average_outside_temperature` | `74.8 °F` | Enabled |
| `sensor.my_tesla_recorded_lifetime_charge_sessions` | `642` | Enabled |
| `sensor.my_tesla_recorded_lifetime_charge_energy_added` | `12684.50 kWh` | Enabled |
| `sensor.my_tesla_recorded_lifetime_charge_energy_used` | `13210.30 kWh` | Enabled |
| `sensor.my_tesla_recorded_lifetime_charge_cost` | `$1268.42` | Enabled |
| `sensor.my_tesla_recorded_lifetime_supercharger_sessions` | `24` | Enabled |
| `sensor.my_tesla_recorded_lifetime_supercharger_energy` | `810.42 kWh` | Enabled |
| `sensor.my_tesla_recorded_lifetime_supercharger_cost` | `$286.55` | Enabled |
| `sensor.my_tesla_recorded_lifetime_idle_sessions` | `940` | Enabled |
| `sensor.my_tesla_recorded_lifetime_idle_time` | `214620.0 min` | Enabled |
| `sensor.my_tesla_recorded_lifetime_idle_energy` | `2480.64 kWh` | Enabled |
| `sensor.my_tesla_recorded_lifetime_idle_battery_used` | `3372.0 %` | Enabled |
| `sensor.my_tesla_recorded_lifetime_idle_rated_range_used` | `10482.40 mi` | Enabled |
| `sensor.my_tesla_recorded_lifetime_sentry_time` | `112430.0 min` | Enabled |
| `sensor.my_tesla_recorded_lifetime_climate_time` | `16842.0 min` | Enabled |
| `sensor.my_tesla_recorded_lifetime_battery_measurements` | `174` | Enabled |
| `sensor.my_tesla_recorded_lifetime_capacity_change` | `-3.48 kWh` | Enabled |
| `sensor.my_tesla_recorded_lifetime_max_range_change` | `-12.20 mi` | Enabled |
| `sensor.my_tesla_recorded_lifetime_max_ideal_range_change` | `-13.40 mi` | Enabled |
| `sensor.my_tesla_oldest_battery_capacity` | `67.19 kWh` | Enabled |
| `sensor.my_tesla_oldest_battery_max_range` | `313.99 mi` | Enabled |
| `sensor.my_tesla_oldest_battery_max_ideal_range` | `276.49 mi` | Enabled |

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

That is the complete v0.4.0 catalog: **247 sensor entities plus 4 tire-pressure warning binary sensors**.

## Update cadence and API load

The configured refresh interval controls the core drive/charging refresh and current-state analytics. To avoid repeatedly requesting slow-changing or larger datasets, other data is cached separately:

- Core drive/charge/current-state data: configured refresh interval (default 5 minutes)
- Historical idles and firmware alerts: about every 1 hour
- Historical state/activity samples: about every 30 minutes
- Battery health, battery-health history, and fleet invoices: about every 6 hours
- Lifetime history: one full backfill on first v0.4.0 refresh, then incremental refreshes about every 6 hours with a 2-day overlap
- Lifetime full reconciliation: about every 30 days
- Last-drive route: fetched when the latest drive changes

Lifetime drive, charge, idle, and battery-health datasets are fetched independently. A failure in one lifetime endpoint preserves the last good cached data for the other datasets rather than discarding the entire lifetime cache.

An optional endpoint failure is isolated from the core drive/charging coordinator when possible, so a temporary battery-health, history, path, firmware, lifetime-history, or fleet-only endpoint problem should not make the main drive sensors unavailable. Authentication failures still trigger Home Assistant's reauthentication flow.

## Recorder and storage considerations

The optional last-drive route entity can expose GPS path points as attributes. It is disabled by default and limits the stored route to at most 200 points to reduce Home Assistant recorder/database growth.

Version 0.4.0 also stores a compact lifetime-history cache using Home Assistant storage. The cache retains only the record IDs/timestamps and numeric/statistical fields required for lifetime calculations. Historical addresses, saved locations, latitude, longitude, and driving-path points are intentionally excluded from the lifetime cache.

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

Version 0.4.0 preserves the existing VIN-based unique IDs for earlier sensors and adds lifetime analytics as additional entities. After updating through HACS, restart Home Assistant so the new entities are registered.

The first v0.4.0 refresh may take longer than normal while Tessie history is backfilled. Once complete, the compact lifetime cache persists across Home Assistant restarts and subsequent lifetime updates are incremental.

Some diagnostic, route, observed-activity, tire-status, fleet-invoice, and lifetime-sync entities are disabled by default. Enable any of them from the vehicle's entity list if you want to use them.

## Migrating from REST YAML sensors

If you already have manually-created Tessie REST sensors, remove or rename conflicting sensors before configuring this integration if you want to avoid Home Assistant assigning `_2` suffixes to duplicate entity IDs.

The normal Tessie vehicle integration can remain installed. Tessie Drive Stats uses the separate `tessie_drive_stats` domain.

## Privacy

The integration stores the Tessie access token in the Home Assistant config entry as required for API access. Diagnostics redact the token and avoid returning street addresses, GPS coordinates, or route points.

The v0.4.0 lifetime cache is privacy-minimized: it stores only fields required to calculate lifetime statistics and intentionally excludes historical addresses, saved-location names, GPS coordinates, and route paths.

Normal Home Assistant entity states may still contain user-requested data such as last-drive locations or navigation destinations. Treat downloaded diagnostics and screenshots according to your own privacy requirements.

## Tessie API

Create an access token from Tessie Developer Settings. Tessie authentication uses an `Authorization: Bearer <token>` header.

### New to Tessie?

If you're signing up for Tessie and would like to support this project, you can use my referral link:

**[Sign up for Tessie with my referral link](https://share.tessie.com/8TNHZg25Zwb)**

*Disclosure: This is a personal Tessie referral link.*

## Development validation

The repository includes synthetic calculation and lifetime-cache tests. GitHub Actions compiles the integration and runs the test suite on repository validation runs. No real VIN, trip address, or access token is included in the test fixtures.

## Version

0.4.0
