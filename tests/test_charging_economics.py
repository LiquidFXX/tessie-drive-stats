"""Tests for v0.6 Charging Economics helpers."""

import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "tessie_drive_stats"
    / "charging_economics.py"
)
spec = importlib.util.spec_from_file_location("tessie_charging_economics", MODULE_PATH)
econ = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(econ)


def charge(
    i,
    *,
    started_at=1000,
    energy_added=18.0,
    energy_used=20.0,
    cost=3.0,
    is_supercharger=False,
):
    return {
        "id": i,
        "started_at": started_at + i,
        "ended_at": started_at + i + 3600,
        "energy_added": energy_added,
        "energy_used": energy_used,
        "cost": cost,
        "is_supercharger": is_supercharger,
    }


def drive(i, *, started_at=1000, miles=10.0, energy=2.5):
    return {
        "id": i,
        "started_at": started_at + i,
        "ended_at": started_at + i + 1200,
        "odometer_distance": miles,
        "energy_used": energy,
    }


def test_charging_efficiency_matches_tessie_definition():
    assert econ.charging_efficiency([charge(1)]) == 90.0
    assert econ.charging_loss([charge(1)]) == 10.0


def test_efficiency_ignores_partial_sessions_instead_of_skewing():
    charges = [charge(1), charge(2, energy_used=None)]
    assert econ.charging_efficiency(charges) == 90.0


def test_average_cost_per_kwh_is_energy_weighted():
    charges = [
        charge(1, energy_used=10, cost=2),
        charge(2, energy_used=30, cost=9),
    ]
    assert econ.average_charging_cost_per_kwh(charges) == 0.275


def test_missing_cost_is_not_treated_as_free():
    charges = [
        charge(1, energy_used=10, cost=2),
        charge(2, energy_used=30, cost=None),
    ]
    assert econ.average_charging_cost_per_kwh(charges) == 0.2
    assert econ.charging_cost_coverage(charges) == 25.0


def test_estimated_drive_cost_uses_real_drive_energy():
    drives = [drive(1, miles=10, energy=2.5), drive(2, miles=20, energy=4.0)]
    assert econ.estimated_driving_cost(drives, 0.20) == 1.30
    assert econ.estimated_drive_cost_per_mile(drives, 0.20) == 0.0433


def test_records_between_uses_half_open_interval():
    records = [
        charge(1, started_at=999),
        charge(2, started_at=1998),
        charge(3, started_at=2997),
    ]
    # Actual starts are 1000, 2000 and 3000 after the helper adds the id.
    selected = econ.records_between(records, 2000, 3000)
    assert [item["id"] for item in selected] == [2]


def test_supercharger_classification_preserves_unknown():
    charges = [
        charge(1, is_supercharger=True),
        charge(2, is_supercharger=False),
        {"id": 3, "started_at": 1003, "energy_used": 20, "cost": 4},
    ]
    assert [c["id"] for c in econ.classified_charges(charges, supercharger=True)] == [1]
    assert [c["id"] for c in econ.classified_charges(charges, supercharger=False)] == [2]


def test_common_coverage_uses_later_history_start():
    charges = [charge(1, started_at=999)]  # starts 1000
    drives = [drive(1, started_at=1999)]  # starts 2000
    assert econ.common_coverage_start(charges, drives) == 2000


def test_percent_change_for_supercharger_premium():
    assert econ.percent_change(0.42, 0.14) == 200.0
    assert econ.percent_change(0.12, 0.15) == -20.0
    assert econ.percent_change(0.12, 0) is None


def test_charging_economics_period_and_lifetime_outputs():
    data = {
        "boundaries": {
            "now": 5000,
            "today": 1000,
            "week": 1000,
            "month": 1000,
            "year": 1000,
        },
        "charges_ytd": [
            charge(1, energy_added=18, energy_used=20, cost=2, is_supercharger=False),
            charge(2, energy_added=27, energy_used=30, cost=12, is_supercharger=True),
        ],
        "drives_ytd": [drive(1, miles=10, energy=2.5), drive(2, miles=20, energy=5.0)],
        "last_charge": charge(2, energy_added=27, energy_used=30, cost=12, is_supercharger=True),
        "last_supercharger": charge(2, energy_added=27, energy_used=30, cost=12, is_supercharger=True),
        "lifetime_charges": [
            charge(1, energy_added=18, energy_used=20, cost=2, is_supercharger=False),
            charge(2, energy_added=27, energy_used=30, cost=12, is_supercharger=True),
        ],
        "lifetime_drives": [
            drive(1, miles=10, energy=2.5),
            drive(2, miles=20, energy=5.0),
        ],
    }

    result = econ.charging_economics(data)
    assert result["charging_efficiency_this_month"] == 90.0
    assert result["average_charging_cost_per_kwh_this_month"] == 0.28
    assert result["charging_cost_coverage_this_month"] == 100.0
    assert result["estimated_driving_cost_this_month"] == 2.10
    assert result["estimated_drive_cost_per_mile_this_month"] == 0.07
    assert result["last_charge_cost_per_kwh"] == 0.4
    assert result["recorded_lifetime_non_supercharger_average_cost_per_kwh"] == 0.1
    assert result["recorded_lifetime_supercharger_average_cost_per_kwh"] == 0.4
    assert result["recorded_lifetime_supercharger_cost_premium"] == 300.0
