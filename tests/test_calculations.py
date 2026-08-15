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
        "energy_used": 2.5,
        "starting_saved_location": "Home",
        "ending_location": "Example Workplace",
    },
]


def test_today_metrics():
    assert calc.drive_count(DRIVES) == 2
    assert calc.drive_miles(DRIVES) == 23.11
    assert calc.drive_energy(DRIVES) == 4.94
    assert calc.drive_time_minutes(DRIVES) == 44.6
    assert calc.drive_efficiency(DRIVES) == 214
    assert calc.drive_battery_used(DRIVES) == 8


def test_latest_drive():
    latest = calc.latest_record(DRIVES)
    assert latest["id"] == 1002
    assert calc.record_distance(latest) == 11.64
    assert calc.record_energy(latest) == 2.44
    assert calc.record_time_minutes(latest) == 23.5
    assert calc.record_efficiency(latest) == 210
    assert calc.record_battery_used(latest) == 4
    assert calc.record_location(latest, ending=True) == "Home"


def test_cost_period_filtering():
    charges = [
        {"started_at": 100, "cost": 1.25},
        {"started_at": 200, "cost": 2.5},
        {"started_at": 300, "cost": None},
    ]
    assert calc.cost_since(charges, 0) == 3.75
    assert calc.cost_since(charges, 150) == 2.5
    assert calc.cost_since(charges, 400) == 0
