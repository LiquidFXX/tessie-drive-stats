# Bundled Lovelace card

Tessie Drive Stats 0.6.3b5 includes a **pre-release bundled Lovelace card**. The card ships inside the integration; a second HACS frontend repository is not required.

0.6.3b4 fixed frontend publication after real Home Assistant testing showed that registering only through `add_extra_js_url` could still leave the dashboard editor unable to resolve `tessie-drive-stats-card`. The integration now registers the card in two ways using the same cache-busted module URL:

- Home Assistant frontend extra-module registration, for compatibility and YAML-managed resource setups.
- An explicit Lovelace module resource when Lovelace resources are storage-managed.

The resource registration loads the existing Lovelace resource store before reading or writing it, updates an older Tessie Drive Stats card URL in place instead of creating duplicates, and falls back to the frontend extra-module path when resources are YAML-managed or not writable.

0.6.3b5 adds the dedicated **Cost to Drive** view. It focuses on the cost of actual driving rather than charge-session spending and uses the existing Charging Economics and drive-period entities already exposed by the integration.

After installing or updating the integration and restarting Home Assistant, add **Tessie Drive Stats** from the dashboard card picker or use YAML:

```yaml
type: custom:tessie-drive-stats-card
view: overview
```

If there is exactly one Tessie Drive Stats vehicle, the card can discover it automatically. For multiple vehicles, use the visual editor's **Vehicle** selector. Advanced YAML users may also provide an existing Tessie Drive Stats entity as an anchor:

```yaml
type: custom:tessie-drive-stats-card
entity: sensor.my_tesla_vehicle_status
view: overview
```

## Card views

The bundled card currently includes nine views:

- `overview` — battery/range/status plus selected-period driving and cost highlights
- `drive` — last-drive details plus a selected-period driving summary
- `efficiency` — Efficiency Intelligence / Drive Energy Factors comparisons
- `cost_to_drive` — selected-period total driving cost, cost per mile, cost per 100 miles, last-drive estimated cost, miles, energy, efficiency, drive time, average speed, drive count, charging rate, and cost coverage
- `charging` — current charging state plus last charge and Supercharger details
- `charging_economics` — selected-period efficiency, losses, cost coverage, rates, and cost per mile
- `battery` — state of charge, range, health, degradation, capacity, pack temperatures, and 30-day changes
- `lifetime` — Tessie-recorded lifetime driving, charging, idle, AP/FSD, battery-history, and estimated driving-cost highlights
- `idle` — selected-period idle/vampire use plus the last idle session

## Options

```yaml
type: custom:tessie-drive-stats-card
view: cost_to_drive
layout: auto
period: this_month
show_header: true
title: Cost to Drive
```

### `view`

One of:

```text
overview
drive
efficiency
cost_to_drive
charging
charging_economics
battery
lifetime
idle
```

### `layout`

- `auto` — responsive default
- `compact` — tighter spacing and denser metric layout
- `wide` — optimized for wider Sections/dashboard placements

### `period`

Used by Overview, Drive, Cost to Drive, Charging Economics, and Idle & Vampire:

```text
today
this_week
this_month
this_year
```

### Cost to Drive calculations

The card uses native Tessie Drive Stats period sensors for total estimated driving cost and estimated cost per mile. **Cost / 100 mi** is displayed as cost per mile × 100. **Last Drive Est. Cost** is a card-level estimate using the selected period's average charging cost per kWh multiplied by the last drive's recorded energy use. Cost coverage is shown so users can see how much of the charging-energy history has a known cost.

These are driving-cost estimates based on the same charging-cost methodology documented for Charging Economics; they are not a direct allocation of a specific charging session to a specific drive.

### `show_header`

Set to `false` to remove the card header.

### `title`

Optional custom title for the selected view.

## Theme behavior

The card intentionally does **not** ship a forced visual theme or fixed color palette. It uses Home Assistant theme variables for card surfaces, text, dividers, primary accents, success states, warning states, and error states.

The card also uses native `ha-card` and `ha-icon` elements and contains no external JavaScript/CSS runtime dependencies.

## Multi-vehicle behavior

The visual editor exposes a Home Assistant config-entry selector filtered to Tessie Drive Stats. When selected, the card resolves its entities from the Home Assistant entity registry using the integration's stable unique IDs, so renamed entities can continue to work.

If no vehicle is selected and exactly one `*_vehicle_status` entity is available, the card falls back to automatic single-vehicle discovery.

## Pre-release installation

HACS normally excludes pre-releases from update checks unless pre-release tracking is enabled. For testing, open the Tessie Drive Stats repository in HACS, use **Redownload**, and choose `0.6.3b5` under **Need a different version?** if it is not offered automatically. Restart Home Assistant after the download and refresh the frontend before testing the card picker.

After restart, storage-mode Lovelace installations should also show a resource beginning with `/tessie_drive_stats/tessie-drive-stats-card.js` in the dashboard resource list. That provides a quick diagnostic that the bundled module has been published.

## Pre-release notes

0.6.3b5 is intended for card layout, frontend-loading, and compatibility testing before the bundled card is promoted to a stable release. Existing sensor and binary-sensor calculations are unchanged; Cost to Drive is a frontend card view built from existing entities plus the two clearly labeled display-only derived values described above.
