"""Tests for calculation helpers using synthetic vehicle history."""

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
        "id": 1002,
        "started_at": 2000,
        "ended_at": 3411,
        "starting_battery": 65,
        "ending_battery": 61,
        "odometer_distance": 11.64,
        "autopilot_distance": 8.25,
        "energy_used": 2.44,
        "starting_location": "Example Workplace",
        "ending_saved_location": "Home",
    },
    {
        "id": 1001,
        "started_at": 500,
        "ended_at": 1763,
        "starting_battery": 70,
        "ending_battery": 66,
        "odometer_distance": 11.47,
        "autopilot_distance": None,
        "energy_used": 2.5,
        "starting_saved_location": "Home",
        "ending_location": "Example Workplace",
    },
]

CHARGES = [
    {
        "id": 2001,
        "started_at": 100,
        "ended_at": 200,
        "is_supercharger": False,
        "energy_added": 8.0,
        "cost": 1.25,
    },
    {
        "id": 2002,
        "started_at": 300,
        "ended_at": 400,
        "is_supercharger": True,
        "energy_added": 40.5,
        "cost": 13.75,
    },
    {
        "id": 2003,
        "started_at": 500,
        "ended_at": 600,
        "is_supercharger": True,
        "energy_added": 22.0,
        "cost": 7.5,
    },
]


def test_today_metrics():
    assert calc.drive_count(DRIVES) == 2
    assert calc.drive_miles(DRIVES) == 23.11
    assert calc.drive_energy(DRIVES) == 4.94
    assert calc.drive_time_minutes(DRIVES) == 44.6
    assert calc.drive_efficiency(DRIVES) == 214
    assert calc.drive_battery_used(DRIVES) == 8


def test_autopilot_metrics():
    assert calc.drive_autopilot_miles(DRIVES) == 8.25
    assert calc.record_autopilot_distance(DRIVES[0]) == 8.25
    assert calc.record_autopilot_distance(DRIVES[1]) is None
    assert calc.drive_autopilot_miles([]) == 0.0
    assert calc.drive_autopilot_miles([{"autopilot_distance": None}]) is None


def test_latest_drive():
    latest = calc.latest_record(DRIVES)
    assert latest["id"] == 1002
    assert calc.record_distance(latest) == 11.64
    assert calc.record_energy(latest) == 2.44
    assert calc.record_time_minutes(latest) == 23.5
    assert calc.record_efficiency(latest) == 210
    assert calc.record_battery_used(latest) == 4
    assert calc.record_location(latest, ending=True) == "Home"


def test_period_filtering():
    assert [r["id"] for r in calc.records_since(DRIVES, 1500)] == [1002]
    assert calc.cost_since(CHARGES, 0) == 22.5
    assert calc.cost_since(CHARGES, 400) == 7.5
    assert calc.cost_since(CHARGES, 700) == 0


def test_supercharger_metrics():
    assert [c["id"] for c in calc.supercharger_records(CHARGES)] == [2002, 2003]
    assert calc.supercharger_count_since(CHARGES, 0) == 2
    assert calc.supercharger_count_since(CHARGES, 400) == 1
    assert calc.supercharger_energy_since(CHARGES, 0) == 62.5
    assert calc.supercharger_energy_since(CHARGES, 400) == 22.0
    assert calc.supercharger_cost_since(CHARGES, 0) == 21.25
    assert calc.supercharger_cost_since(CHARGES, 400) == 7.5
