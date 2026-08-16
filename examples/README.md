# Tessie Drive Stats — Card Examples

This page is the screenshot gallery for Home Assistant cards built with Tessie Drive Stats entities.

The current example set uses a **Tesla-inspired dark UI**: charcoal panels, white/gray typography, Tesla red accents, compact metric tiles, and green/yellow/red reserved for status conditions.

The screenshots are examples only. Entity IDs, values, units, themes, and card layouts will vary between Home Assistant installations.

> **Privacy note:** Before publishing a screenshot, check it for home/work addresses, navigation destinations, VINs, GPS coordinates, access tokens, or any other personal information. Location data should be cropped or redacted before it is committed.

## Tesla UI gallery

Use this image for an overview of the complete example set.

<!--
![Tesla UI card gallery](screenshots/tesla-ui-gallery.jpg)
-->

Suggested filename: `screenshots/tesla-ui-gallery.jpg`

## Dashboard header

The vehicle header shows the vehicle name plus compact status modules for vehicle state, battery level, range, charging state, and outside temperature.

<!--
![Tesla UI dashboard header](screenshots/dashboard-header.png)
-->

Suggested filename: `screenshots/dashboard-header.png`

## Vehicle

Live vehicle information including connection state, battery/range, energy remaining, phantom drain, temperatures, odometer, and lifetime energy.

<!--
![Vehicle card](screenshots/vehicle.png)
-->

Suggested filename: `screenshots/vehicle.png`

## Charging

Current charging state, charge limit, charge rate, charger power, and time to full.

<!--
![Charging card](screenshots/charging.png)
-->

Suggested filename: `screenshots/charging.png`

## Driving — Today

<!--
![Today driving card](screenshots/driving-today.png)
-->

Suggested filename: `screenshots/driving-today.png`

## Driving — This Week

<!--
![This Week driving card](screenshots/driving-week.png)
-->

Suggested filename: `screenshots/driving-week.png`

## Driving — This Month

<!--
![This Month driving card](screenshots/driving-month.png)
-->

Suggested filename: `screenshots/driving-month.png`

## Driving — This Year

<!--
![This Year driving card](screenshots/driving-year.png)
-->

Suggested filename: `screenshots/driving-year.png`

## Last Drive

Shows the most recent completed drive, including distance, drive time, energy, efficiency, AP/FSD distance, battery use, speed, temperatures, range use, route information, and optional path data.

**Public screenshots should hide exact start/destination addresses.**

<!--
![Last Drive card](screenshots/last-drive.png)
-->

Suggested filename: `screenshots/last-drive.png`

## Since Last Charge

Shows battery, energy, and range consumption since the most recent charge, including driving vs. non-driving use.

<!--
![Since Last Charge card](screenshots/since-last-charge.png)
-->

Suggested filename: `screenshots/since-last-charge.png`

## Battery Health & Range

Shows battery health, degradation, current/original capacity, maximum range, module temperatures, and long-term capacity/range changes.

<!--
![Battery health card](screenshots/battery-health.png)
-->

Suggested filename: `screenshots/battery-health.png`

## Idle / Vampire Drain — Today

<!--
![Idle Today card](screenshots/idle-today.png)
-->

Suggested filename: `screenshots/idle-today.png`

## Idle / Vampire Drain — This Week

<!--
![Idle This Week card](screenshots/idle-week.png)
-->

Suggested filename: `screenshots/idle-week.png`

## Idle / Vampire Drain — This Month

<!--
![Idle This Month card](screenshots/idle-month.png)
-->

Suggested filename: `screenshots/idle-month.png`

## Idle / Vampire Drain — This Year

<!--
![Idle This Year card](screenshots/idle-year.png)
-->

Suggested filename: `screenshots/idle-year.png`

## Last Idle

<!--
![Last Idle card](screenshots/last-idle.png)
-->

Suggested filename: `screenshots/last-idle.png`

## Charging Costs

<!--
![Charging Costs card](screenshots/charging-costs.png)
-->

Suggested filename: `screenshots/charging-costs.png`

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

## Navigation

Shows active Tesla navigation data including destination, distance/ETA, traffic delay, and estimated battery at arrival.

<!--
![Navigation card](screenshots/navigation.png)
-->

Suggested filename: `screenshots/navigation.png`

## Software & Alerts

Shows Tesla software version, update state/progress, firmware-alert information, and observed activity statistics.

<!--
![Software and alerts card](screenshots/software-alerts.png)
-->

Suggested filename: `screenshots/software-alerts.png`

## Additional Data

The dashboard's catch-all section can display newly enabled or otherwise uncategorized Tessie Drive Stats entities.

<!--
![Additional Data card](screenshots/additional-data.png)
-->

Suggested filename: `screenshots/additional-data.png`

## Adding screenshots

1. Add images to `examples/screenshots/` using the suggested filenames above.
2. Remove the `<!--` and `-->` around the corresponding Markdown image line in this file.
3. Commit the image and Markdown change together.

For consistency, crop screenshots tightly around the card or dashboard, use PNG where practical, and redact private location data before publishing.
