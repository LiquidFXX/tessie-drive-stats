# Bundled Lovelace card

Tessie Drive Stats 0.6.3b1 introduces a **pre-release bundled Lovelace card**. The card ships inside the integration; a second HACS frontend repository is not required.

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

The bundled card currently includes eight views:

- `overview` — battery/range/status plus selected-period driving and cost highlights
- `drive` — last-drive details plus a selected-period driving summary
- `efficiency` — Efficiency Intelligence / Drive Energy Factors comparisons
- `charging` — current charging state plus last charge and Supercharger details
- `charging_economics` — selected-period efficiency, losses, cost coverage, rates, and cost per mile
- `battery` — state of charge, range, health, degradation, capacity, pack temperatures, and 30-day changes
- `lifetime` — Tessie-recorded lifetime driving, charging, idle, AP/FSD, and battery-history highlights
- `idle` — selected-period idle/vampire use plus the last idle session

## Options

```yaml
type: custom:tessie-drive-stats-card
view: charging_economics
layout: auto
period: this_month
show_header: true
title: Charging Economics
```

### `view`

One of:

```text
overview
drive
efficiency
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

Used by Overview, Drive, Charging Economics, and Idle & Vampire:

```text
today
this_week
this_month
this_year
```

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

## Pre-release notes

0.6.3b1 is intended for card layout and compatibility testing before the bundled card is promoted to a stable release. Existing sensor and binary-sensor calculations are unchanged by this frontend addition.
