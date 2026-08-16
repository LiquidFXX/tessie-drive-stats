"""Tests for Tessie Drive Stats calculation helpers."""

import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "tessie_drive_stats"
    / "calculations.py"
)
spec = importlib.util.spec_from_file_location("tessie_calculations", MODULE_PATH)
calc = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(calc)

DRIVES = [
    {
        "id": 2,
        "started_at": 2000,
        "ended_at": 3200,
        "starting_battery": 70,
        "ending_battery": 65,
        "odometer_distance": 10,
        "autopilot_distance": 7.5,
        "energy_used": 2.5,
        "average_speed": 30,
        "max_speed": 62,
        "rated_range_used": 12,
        "average_inside_temperature": 70,
        "average_outside_temperature": 80,
    },
    {
        "id": 1,
        "started_at": 1000,
        "ended_at": 1600,
        "starting_battery": 80,
        "ending_battery": 77,
        "odometer_distance": 5,
        "autopilot_distance": 2,
        "energy_used": 1,
        "average_speed": 30,
        "max_speed": 55,
        "rated_range_used": 6,
        "average_inside_temperature": 68,
        "average_outside_temperature": 76,
    },
]

IDLES = [
    {
        "started_at": 100,
        "ended_at": 3700,
        "starting_battery": 80,
        "ending_battery": 78,
        "energy_used": 1.5,
        "rated_range_used": 5,
        "sentry_fraction": 0.5,
        "climate_fraction": 0.25,
    },
    {
        "started_at": 4000,
        "ended_at": 5800,
        "starting_battery": 78,
        "ending_battery": 77,
        "energy_used": 0.6,
        "rated_range_used": 2,
        "sentry_fraction": 1,
        "climate_fraction": 0,
    },
]


def test_drive_totals_and_derived_metrics():
    assert calc.drive_count(DRIVES) == 2
    assert calc.drive_miles(DRIVES) == 15
    assert calc.drive_energy(DRIVES) == 3.5
    assert calc.drive_time_minutes(DRIVES) == 30
    assert calc.drive_efficiency(DRIVES) == 233
    assert calc.drive_battery_used(DRIVES) == 8
    assert calc.drive_autopilot_miles(DRIVES) == 9.5
    assert calc.drive_average_speed(DRIVES) == 30
    assert calc.drive_max_speed(DRIVES) == 62
    assert calc.longest_drive(DRIVES) == 10
    assert calc.drive_sum_field(DRIVES, "rated_range_used") == 18


def test_autopilot_null_is_preserved():
    drives = [{"odometer_distance": 2, "autopilot_distance": None}]
    assert calc.drive_autopilot_miles(drives) is None
    assert calc.record_autopilot_distance(drives[0]) is None


def test_idle_analytics():
    assert calc.idle_count(IDLES) == 2
    assert calc.idle_time_minutes(IDLES) == 90
    assert calc.idle_energy(IDLES) == 2.1
    assert calc.idle_battery_used(IDLES) == 3
    assert calc.idle_rated_range_used(IDLES) == 7
    # 60 min * .5 + 30 min * 1
    assert calc.idle_fraction_time_minutes(IDLES, "sentry_fraction") == 60
    # 60 min * .25
    assert calc.idle_fraction_time_minutes(IDLES, "climate_fraction") == 15
    assert calc.record_idle_fraction_percent(IDLES[0], "sentry_fraction") == 50


def test_consumption_breakdown():
    consumption = {
        "energy_used": 7.5,
        "energy_used_by_driving": 5,
        "battery_percent_used": 10,
        "battery_percent_used_by_driving": 6,
    }
    assert calc.consumption_non_driving(consumption, "energy_used", "energy_used_by_driving") == 2.5
    assert calc.consumption_non_driving(consumption, "battery_percent_used", "battery_percent_used_by_driving") == 4
    assert calc.consumption_driving_share(consumption) == 66.7


def test_supercharger_and_cost_helpers():
    charges = [
        {"started_at": 100, "cost": 1.25, "energy_added": 10, "is_supercharger": True},
        {"started_at": 200, "cost": 2.50, "energy_added": 20, "is_supercharger": False},
        {"started_at": 300, "cost": 3.00, "energy_added": 30, "is_supercharger": "true"},
    ]
    assert calc.cost_since(charges, 0) == 6.75
    assert calc.supercharger_count_since(charges, 0) == 2
    assert calc.supercharger_energy_since(charges, 0) == 40
    assert calc.supercharger_cost_since(charges, 0) == 4.25


def test_activity_summary():
    states = [
        {"timestamp": 0, "state": "asleep"},
        {"timestamp": 600, "state": "online"},
        {"timestamp": 1200, "state": "waiting_for_sleep"},
        {"timestamp": 1800, "state": "asleep"},
    ]
    result = calc.activity_summary(states, 0, 2400)
    assert result["asleep_minutes"] == 20
    assert result["awake_minutes"] == 10
    assert result["waiting_for_sleep_minutes"] == 10
    assert result["wakeups"] == 1


def test_battery_health_change():
    records = [
        {"timestamp": 100, "capacity": 75.0, "max_range": 300},
        {"timestamp": 200, "capacity": 74.5, "max_range": 298},
    ]
    assert calc.measurement_change(records, "capacity") == -0.5
    assert calc.measurement_change(records, "max_range") == -2
    assert len(calc.measurements_since(records, 150)) == 1


def test_path_helpers_and_simplification():
    points = [
        {"timestamp": 1, "latitude": 1, "longitude": 1, "autopilot": "Standby"},
        {"timestamp": 2, "latitude": 2, "longitude": 2, "autopilot": "Active"},
        {"timestamp": 3, "latitude": 3, "longitude": 3, "autopilot": "Off"},
        {"timestamp": 4, "latitude": 4, "longitude": 4, "autopilot": "Engaged"},
    ]
    assert calc.path_autopilot_share(points) == 50
    simplified = calc.simplify_path(points, max_points=3)
    assert len(simplified) <= 3
    assert "latitude" in simplified[0]


def test_invoice_helpers():
    invoices = [
        {"vin": "ABC", "total_cost": 10, "idle_fees": 1},
        {"vin": "DEF", "total_cost": 99, "idle_fees": 9},
        {"vin": "abc", "total_cost": 20, "idle_fees": 0},
    ]
    filtered = calc.invoice_records_for_vin(invoices, "ABC")
    assert len(filtered) == 2
    assert calc.invoice_sum(filtered, "total_cost") == 30
