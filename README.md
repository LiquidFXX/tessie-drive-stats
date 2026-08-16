# Tessie Drive Stats for Home Assistant

A HACS-ready Home Assistant custom integration for Tesla analytics backed by Tessie. It turns Tessie drive, charging, idle, consumption, battery, tire, navigation, software, historical-state, and optional fleet-invoice data into native Home Assistant entities.

Tessie Drive Stats is intended to complement the normal Tessie/Home Assistant vehicle integration. It focuses on history, totals, derived analytics, and diagnostic data rather than vehicle controls.

## Highlights

- UI setup; no REST YAML or `secrets.yaml` entry is required.
- Works with any Tesla available to the supplied Tessie access token.
- Supports multiple vehicles by adding one integration entry per VIN.
- Automatically fetches the vehicle name from Tessie during setup.
- Uses the Tessie vehicle name for the Home Assistant device/entity naming while retaining the VIN as the permanent internal identifier.
- Configurable refresh interval (1–60 minutes; default 5).
- Configurable first day of week (default Monday).
- Uses Home Assistant's configured timezone for day/week/month/year boundaries.
- Preserves the v0.2 entity unique IDs so existing dashboards do not need to be rebuilt.
- Adds more than 200 sensor definitions plus tire-pressure warning binary sensors. Niche, recorder-heavy, best-effort, and fleet-only entities are disabled by default where appropriate.
- Diagnostics redact the Tessie access token and intentionally omit addresses, coordinates, and driving-path points.

## Analytics included

### Driving: today / week / month / year

- Drive count
- Miles driven
- Energy used
- Driving time
- Aggregate efficiency
- Combined AP/FSD miles
- Average speed
- Maximum speed
- Longest drive
- Rated range used *(diagnostic, disabled by default)*
- Average inside/outside temperature *(diagnostic, disabled by default)*

Tessie exposes one drive-history field named `autopilot_distance`. It does not distinguish legacy Autopilot from FSD, so the integration deliberately reports **combined AP/FSD distance** rather than inventing a split Tessie does not provide.

### Last drive

- Distance, energy, duration, efficiency
- Combined AP/FSD distance
- Start and destination
- Starting/ending battery and battery used
- Average and maximum speed
- Inside/outside temperature
- Rated range used
- Drive tag
- Driving-path point count and a recorder-friendly, decimated route in attributes *(disabled by default)*
- Best-effort AP-active share calculated from detailed route samples *(disabled by default)*

### Charging and Supercharging

- Total charging cost today / week / month / year
- Supercharger session count today / week / month / year
- Supercharger energy today / week / month / year
- Supercharger cost today / week / month / year
- Last charge cost, energy added, and location
- Last Supercharger cost, energy added, and location

Charging cost totals use Tessie's recorded session `cost`; the integration does not invent a utility rate.

### Idle / vampire drain

Tessie defines an idle as a period when the vehicle is not driving or charging. The integration exposes:

- Idle sessions today / week / month / year
- Idle duration today / week / month / year
- Idle energy used today / week / month / year
- Idle battery loss today / week / month / year
- Rated range lost while idle
- Estimated idle time attributable to Sentry Mode
- Estimated idle time attributable to climate usage
- Last idle duration, energy, battery loss, range loss, Sentry share, climate share, and location
- Last-idle-state battery/range *(diagnostic, disabled by default)*

### Consumption since last charge

- Last charge timestamp
- Distance driven since charge
- Total battery percentage used
- Battery percentage used by driving
- Non-driving battery percentage used
- Rated/ideal range used and driving-only portions
- Total energy used
- Driving energy used
- Non-driving energy used
- Driving-energy share

This makes it easier to separate energy used to move the car from parked/climate/Sentry/other consumption.

### Current battery telemetry

- Battery level
- Rated range
- Ideal range
- Tessie phantom-drain percentage
- Energy remaining
- Lifetime energy used
- Pack current *(diagnostic, disabled by default)*
- Pack voltage *(diagnostic, disabled by default)*
- Minimum/maximum battery-module temperature
- Battery-module temperature spread

### Battery health and history

- Battery health
- Battery degradation
- Current capacity
- Original capacity
- Maximum rated range
- Maximum ideal range
- Battery-health sample count for the year
- 30-day and year-to-date capacity change
- 30-day and year-to-date maximum-range change

Battery-health data changes slowly and is refreshed on a longer cadence than normal drive data.

### Tire pressure

- Front-left, front-right, rear-left, and rear-right pressure
- Tessie pressure status (`unknown`, `low`, `normal`) *(diagnostic status sensors disabled by default)*
- Four `problem` binary sensors for low tire pressure

### Vehicle, navigation, charging, climate, and software state

- Vehicle sleep status (`awake`, `waiting_for_sleep`, `asleep`)
- Odometer
- Vehicle/software version and software-update state
- Navigation destination
- Miles/minutes/traffic delay to arrival
- Estimated battery at arrival
- Current charging state, rate, power, charge limit, and time to full
- Current inside/outside temperature
- Connection status

These are read-only supporting entities. Tessie Drive Stats does not add vehicle controls.

### Firmware alerts

- Alert count
- Latest firmware alert
- Latest alert timestamp
- Latest alert description and recent fleet count in attributes

### Observed sleep/activity analytics

Historical state samples are used for best-effort estimates of:

- Observed awake time today
- Observed asleep time today
- Observed waiting-for-sleep time today
- Observed wakeups today

These entities are disabled by default because historical sampling can only estimate transitions between observations; they should not be treated as exact accounting data.

### Fleet-only charging invoices

Tessie's detailed charging-invoice API is restricted to eligible fleet accounts. The integration supports it without making it a dependency for normal users.

When available, optional entities include:

- Invoice access status
- Invoice count this year
- Invoice Supercharger energy
- Charging fees
- Idle fees
- Total invoice cost
- Last invoice total and cost/kWh
- Last invoice metadata in attributes

These entities are disabled by default. A personal Tessie account continues to work normally when the invoice endpoint is unavailable.

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

## Vehicle naming

The setup form asks for a Tessie access token and VIN. The integration resolves the vehicle's Tessie display name automatically. Home Assistant uses that name for the device and for new entity IDs, while the VIN remains the stable unique ID/device identifier.

For example, a vehicle Tessie names **My Tesla** may receive entity IDs such as:

```text
sensor.my_tesla_miles_today
sensor.my_tesla_idle_energy_today
sensor.my_tesla_battery_health
```

Home Assistant preserves entity IDs that were already registered, so renaming a vehicle does not necessarily rename existing entity IDs.

## Example entity IDs

The entity IDs below are examples for a vehicle named **My Tesla**. Home Assistant generates the vehicle portion of the entity ID from the device/entity naming in your installation, so your prefix may differ (for example, `sensor.car_coaster_...`). The suffixes listed below match the integration's v0.3.0 entity keys.

Entities marked `# disabled by default` can be enabled from **Settings → Devices & services → Tessie Drive Stats → your vehicle → Entities**.

### Driving and last drive

```text
sensor.my_tesla_drives_today
sensor.my_tesla_miles_today
sensor.my_tesla_energy_today
sensor.my_tesla_drive_time_today
sensor.my_tesla_efficiency_today
sensor.my_tesla_battery_used_today
sensor.my_tesla_autopilot_fsd_miles_today
sensor.my_tesla_average_speed_today
sensor.my_tesla_max_speed_today
sensor.my_tesla_longest_drive_today
sensor.my_tesla_rated_range_used_today  # disabled by default
sensor.my_tesla_average_inside_temperature_today  # disabled by default
sensor.my_tesla_average_outside_temperature_today  # disabled by default
sensor.my_tesla_drives_this_week
sensor.my_tesla_miles_this_week
sensor.my_tesla_energy_this_week
sensor.my_tesla_drive_time_this_week
sensor.my_tesla_efficiency_this_week
sensor.my_tesla_autopilot_fsd_miles_this_week
sensor.my_tesla_average_speed_this_week
sensor.my_tesla_max_speed_this_week
sensor.my_tesla_longest_drive_this_week
sensor.my_tesla_rated_range_used_this_week  # disabled by default
sensor.my_tesla_average_inside_temperature_this_week  # disabled by default
sensor.my_tesla_average_outside_temperature_this_week  # disabled by default
sensor.my_tesla_drives_this_month
sensor.my_tesla_miles_this_month
sensor.my_tesla_energy_this_month
sensor.my_tesla_drive_time_this_month
sensor.my_tesla_efficiency_this_month
sensor.my_tesla_autopilot_fsd_miles_this_month
sensor.my_tesla_average_speed_this_month
sensor.my_tesla_max_speed_this_month
sensor.my_tesla_longest_drive_this_month
sensor.my_tesla_rated_range_used_this_month  # disabled by default
sensor.my_tesla_average_inside_temperature_this_month  # disabled by default
sensor.my_tesla_average_outside_temperature_this_month  # disabled by default
sensor.my_tesla_drives_this_year
sensor.my_tesla_miles_this_year
sensor.my_tesla_energy_this_year
sensor.my_tesla_drive_time_this_year
sensor.my_tesla_efficiency_this_year
sensor.my_tesla_autopilot_fsd_miles_this_year
sensor.my_tesla_average_speed_this_year
sensor.my_tesla_max_speed_this_year
sensor.my_tesla_longest_drive_this_year
sensor.my_tesla_rated_range_used_this_year  # disabled by default
sensor.my_tesla_average_inside_temperature_this_year  # disabled by default
sensor.my_tesla_average_outside_temperature_this_year  # disabled by default
sensor.my_tesla_last_drive_miles
sensor.my_tesla_last_drive_autopilot_fsd_miles
sensor.my_tesla_last_drive_energy
sensor.my_tesla_last_drive_time
sensor.my_tesla_last_drive_efficiency
sensor.my_tesla_last_drive_start
sensor.my_tesla_last_drive_destination
sensor.my_tesla_last_drive_starting_battery
sensor.my_tesla_last_drive_ending_battery
sensor.my_tesla_last_drive_battery_used
sensor.my_tesla_last_drive_average_speed
sensor.my_tesla_last_drive_max_speed
sensor.my_tesla_last_drive_inside_temperature
sensor.my_tesla_last_drive_outside_temperature
sensor.my_tesla_last_drive_rated_range_used
sensor.my_tesla_last_drive_tag
sensor.my_tesla_last_drive_path_points  # disabled by default
sensor.my_tesla_last_drive_path_autopilot_share  # disabled by default
```

### Charging, Supercharging, and idle

```text
sensor.my_tesla_cost_today
sensor.my_tesla_supercharger_sessions_today
sensor.my_tesla_supercharger_energy_today
sensor.my_tesla_supercharger_cost_today
sensor.my_tesla_cost_this_week
sensor.my_tesla_supercharger_sessions_this_week
sensor.my_tesla_supercharger_energy_this_week
sensor.my_tesla_supercharger_cost_this_week
sensor.my_tesla_cost_this_month
sensor.my_tesla_supercharger_sessions_this_month
sensor.my_tesla_supercharger_energy_this_month
sensor.my_tesla_supercharger_cost_this_month
sensor.my_tesla_cost_this_year
sensor.my_tesla_supercharger_sessions_this_year
sensor.my_tesla_supercharger_energy_this_year
sensor.my_tesla_supercharger_cost_this_year
sensor.my_tesla_last_charge_cost
sensor.my_tesla_last_charge_energy_added
sensor.my_tesla_last_charge_location
sensor.my_tesla_last_supercharger_cost
sensor.my_tesla_last_supercharger_energy_added
sensor.my_tesla_last_supercharger_location
sensor.my_tesla_idle_sessions_today
sensor.my_tesla_idle_time_today
sensor.my_tesla_idle_energy_today
sensor.my_tesla_idle_battery_used_today
sensor.my_tesla_idle_rated_range_used_today
sensor.my_tesla_idle_sentry_time_today
sensor.my_tesla_idle_climate_time_today
sensor.my_tesla_idle_sessions_this_week
sensor.my_tesla_idle_time_this_week
sensor.my_tesla_idle_energy_this_week
sensor.my_tesla_idle_battery_used_this_week
sensor.my_tesla_idle_rated_range_used_this_week
sensor.my_tesla_idle_sentry_time_this_week
sensor.my_tesla_idle_climate_time_this_week
sensor.my_tesla_idle_sessions_this_month
sensor.my_tesla_idle_time_this_month
sensor.my_tesla_idle_energy_this_month
sensor.my_tesla_idle_battery_used_this_month
sensor.my_tesla_idle_rated_range_used_this_month
sensor.my_tesla_idle_sentry_time_this_month
sensor.my_tesla_idle_climate_time_this_month
sensor.my_tesla_idle_sessions_this_year
sensor.my_tesla_idle_time_this_year
sensor.my_tesla_idle_energy_this_year
sensor.my_tesla_idle_battery_used_this_year
sensor.my_tesla_idle_rated_range_used_this_year
sensor.my_tesla_idle_sentry_time_this_year
sensor.my_tesla_idle_climate_time_this_year
sensor.my_tesla_last_idle_time
sensor.my_tesla_last_idle_energy
sensor.my_tesla_last_idle_battery_used
sensor.my_tesla_last_idle_rated_range_used
sensor.my_tesla_last_idle_sentry_share
sensor.my_tesla_last_idle_climate_share
sensor.my_tesla_last_idle_location
sensor.my_tesla_last_idle_starting_battery
sensor.my_tesla_last_idle_ending_battery
sensor.my_tesla_last_idle_state_battery_level  # disabled by default
sensor.my_tesla_last_idle_state_range  # disabled by default
```

### Consumption and battery

```text
sensor.my_tesla_consumption_last_charge_at
sensor.my_tesla_distance_since_charge
sensor.my_tesla_battery_used_since_charge
sensor.my_tesla_battery_used_by_driving_since_charge
sensor.my_tesla_battery_used_non_driving_since_charge
sensor.my_tesla_rated_range_used_since_charge
sensor.my_tesla_rated_range_used_by_driving_since_charge
sensor.my_tesla_ideal_range_used_since_charge  # disabled by default
sensor.my_tesla_ideal_range_used_by_driving_since_charge  # disabled by default
sensor.my_tesla_energy_used_since_charge
sensor.my_tesla_energy_used_by_driving_since_charge
sensor.my_tesla_energy_used_non_driving_since_charge
sensor.my_tesla_driving_energy_share_since_charge
sensor.my_tesla_battery_level_current
sensor.my_tesla_battery_range_current
sensor.my_tesla_ideal_battery_range_current
sensor.my_tesla_phantom_drain
sensor.my_tesla_energy_remaining
sensor.my_tesla_lifetime_energy_used
sensor.my_tesla_pack_current  # disabled by default
sensor.my_tesla_pack_voltage  # disabled by default
sensor.my_tesla_battery_module_temp_min
sensor.my_tesla_battery_module_temp_max
sensor.my_tesla_battery_module_temp_spread
sensor.my_tesla_battery_health
sensor.my_tesla_battery_degradation
sensor.my_tesla_battery_capacity
sensor.my_tesla_battery_original_capacity
sensor.my_tesla_battery_max_range
sensor.my_tesla_battery_max_ideal_range
sensor.my_tesla_battery_health_measurements_this_year
sensor.my_tesla_battery_capacity_change_30_days
sensor.my_tesla_battery_capacity_change_this_year
sensor.my_tesla_battery_max_range_change_30_days
sensor.my_tesla_battery_max_range_change_this_year
```

### Vehicle, tires, software, activity, and fleet

```text
sensor.my_tesla_vehicle_status
sensor.my_tesla_odometer_current
sensor.my_tesla_software_version
sensor.my_tesla_software_update_status
sensor.my_tesla_software_update_version
sensor.my_tesla_software_update_download
sensor.my_tesla_software_update_install
sensor.my_tesla_navigation_destination
sensor.my_tesla_navigation_miles_to_arrival
sensor.my_tesla_navigation_minutes_to_arrival
sensor.my_tesla_navigation_traffic_delay
sensor.my_tesla_navigation_energy_at_arrival
sensor.my_tesla_charging_state_current
sensor.my_tesla_charge_rate_current
sensor.my_tesla_charger_power_current
sensor.my_tesla_charge_limit
sensor.my_tesla_time_to_full_charge
sensor.my_tesla_inside_temperature_current
sensor.my_tesla_outside_temperature_current
sensor.my_tesla_connection_status
sensor.my_tesla_tire_pressure_front_left
sensor.my_tesla_tire_status_front_left  # disabled by default
sensor.my_tesla_tire_pressure_front_right
sensor.my_tesla_tire_status_front_right  # disabled by default
sensor.my_tesla_tire_pressure_rear_left
sensor.my_tesla_tire_status_rear_left  # disabled by default
sensor.my_tesla_tire_pressure_rear_right
sensor.my_tesla_tire_status_rear_right  # disabled by default
sensor.my_tesla_firmware_alert_count
sensor.my_tesla_latest_firmware_alert
sensor.my_tesla_latest_firmware_alert_at
sensor.my_tesla_observed_awake_time_today  # disabled by default
sensor.my_tesla_observed_asleep_time_today  # disabled by default
sensor.my_tesla_observed_waiting_for_sleep_time_today  # disabled by default
sensor.my_tesla_observed_wakeups_today  # disabled by default
sensor.my_tesla_charging_invoice_access  # disabled by default
sensor.my_tesla_supercharger_invoice_count_this_year  # disabled by default
sensor.my_tesla_supercharger_invoice_energy_this_year  # disabled by default
sensor.my_tesla_supercharger_invoice_charging_fees_this_year  # disabled by default
sensor.my_tesla_supercharger_invoice_idle_fees_this_year  # disabled by default
sensor.my_tesla_supercharger_invoice_total_cost_this_year  # disabled by default
sensor.my_tesla_last_supercharger_invoice_cost  # disabled by default
sensor.my_tesla_last_supercharger_invoice_cost_per_kwh  # disabled by default
```

### Tire-pressure warning binary sensors

```text
binary_sensor.my_tesla_tire_pressure_low_front_left
binary_sensor.my_tesla_tire_pressure_low_front_right
binary_sensor.my_tesla_tire_pressure_low_rear_left
binary_sensor.my_tesla_tire_pressure_low_rear_right
```

That is the complete v0.3.0 catalog: **206 sensor entities plus 4 tire-pressure warning binary sensors**.

## Install through HACS as a custom repository

1. Open **HACS → Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/LiquidFXX/tessie-drive-stats` and select **Integration**.
4. Install **Tessie Drive Stats**.
5. Restart Home Assistant.
6. Open **Settings → Devices & services → Add integration**.
7. Search for **Tessie Drive Stats** and enter the Tessie access token and vehicle VIN.

To add another vehicle, add Tessie Drive Stats again with its VIN.

You may paste either the raw Tessie token or `Bearer <token>`; the integration normalizes both forms.

## Updating from an earlier beta

Version 0.3.0 preserves the existing VIN-based unique IDs for the v0.2 sensors and adds the new analytics as additional entities. After updating through HACS, restart Home Assistant so the new `sensor` and `binary_sensor` platforms/entities are registered.

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
