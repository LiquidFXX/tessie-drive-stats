# Tessie Drive Stats — Card Examples

This page is the screenshot gallery for Home Assistant cards built with Tessie Drive Stats entities.

The screenshots are examples only. Entity IDs, values, units, themes, and card layouts will vary between Home Assistant installations.

> **Privacy note:** Before posting a screenshot, check it for home/work addresses, navigation destinations, VINs, GPS coordinates, access tokens, or any other personal information.

## Full analytics dashboard

Use this section for a screenshot of the complete Tessie Drive Stats analytics dashboard.

<!--
![Full Tessie Drive Stats dashboard](screenshots/full-dashboard.png)
-->

Suggested filename: `screenshots/full-dashboard.png`

## Last Drive

Shows the most recent completed drive, including route, distance, drive time, energy, efficiency, AP/FSD distance, battery use, speed, and other available trip data.

<!--
![Last Drive card](screenshots/last-drive.png)
-->

Suggested filename: `screenshots/last-drive.png`

## AP / FSD

Shows combined AP/FSD distance from Tessie's `autopilot_distance` field for today, week, month, year, and the most recent drive.

<!--
![AP FSD card](screenshots/ap-fsd.png)
-->

Suggested filename: `screenshots/ap-fsd.png`

## Driving Overview

Use this for cards showing drive count, miles, drive time, energy, efficiency, average speed, maximum speed, longest drive, and period totals.

<!--
![Driving overview card](screenshots/driving-overview.png)
-->

Suggested filename: `screenshots/driving-overview.png`

## Battery Health & Range

Shows battery health, degradation, current/original capacity, maximum range, current range, battery-module temperatures, and long-term battery trends.

<!--
![Battery health card](screenshots/battery-health.png)
-->

Suggested filename: `screenshots/battery-health.png`

## Since Last Charge

Shows energy and battery use since the last charge, including driving vs. non-driving consumption and range usage.

<!--
![Since Last Charge card](screenshots/since-last-charge.png)
-->

Suggested filename: `screenshots/since-last-charge.png`

## Idle / Vampire Drain

Shows parked energy use, idle time, battery loss, rated range loss, Sentry usage, climate usage, and last-idle details.

<!--
![Idle vampire drain card](screenshots/idle-vampire-drain.png)
-->

Suggested filename: `screenshots/idle-vampire-drain.png`

## Charging

Use this section for current charging state, charge rate, charger power, charge limit, time to full, charging cost, and last-charge information.

<!--
![Charging card](screenshots/charging.png)
-->

Suggested filename: `screenshots/charging.png`

## Supercharging

Shows Supercharger sessions, energy, costs, last Supercharger details, and optional fleet-invoice data when available.

<!--
![Supercharging card](screenshots/supercharging.png)
-->

Suggested filename: `screenshots/supercharging.png`

## Tire Pressure

Shows all four tire pressures and low-pressure warning binary sensors.

<!--
![Tire pressure card](screenshots/tire-pressure.png)
-->

Suggested filename: `screenshots/tire-pressure.png`

## Navigation & Vehicle Status

Use this section for vehicle awake/asleep state, connection status, active route, ETA, traffic delay, and estimated battery at arrival.

<!--
![Navigation and vehicle status card](screenshots/navigation-vehicle.png)
-->

Suggested filename: `screenshots/navigation-vehicle.png`

## Software & Alerts

Shows Tesla software version, update state/progress, firmware-alert information, and observed activity statistics.

<!--
![Software and alerts card](screenshots/software-alerts.png)
-->

Suggested filename: `screenshots/software-alerts.png`

## Adding a screenshot

1. Add the image to `examples/screenshots/` using the suggested filename above.
2. Return to this file.
3. Remove the `<!--` and `-->` around that screenshot's Markdown image line.
4. Commit both changes together.

For example:

```markdown
![Last Drive card](screenshots/last-drive.png)
```

For consistency, crop screenshots tightly around the card or dashboard, avoid exposing private location data, and use PNG where practical.
