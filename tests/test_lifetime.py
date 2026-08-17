"""Tests for lifetime Tessie history helpers."""

import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "tessie_drive_stats"
    / "lifetime.py"
)
spec = importlib.util.spec_from_file_location("tessie_lifetime", MODULE_PATH)
life = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(life)


def test_compactors_remove_private_location_data():
    drive = {
        "id": 1,
        "started_at": 100,
        "ended_at": 200,
        "starting_location": "Private address",
        "starting_latitude": 32.0,
        "ending_longitude": -80.0,
        "odometer_distance": 10,
        "energy_used": 2.5,
    }
    compact = life.compact_drive(drive)
    assert compact["id"] == 1
    assert compact["odometer_distance"] == 10
    assert "starting_location" not in compact
    assert "starting_latitude" not in compact
    assert "ending_longitude" not in compact


def test_merge_records_replaces_overlap_by_id():
    existing = {
        "1": {"id": 1, "started_at": 100, "cost": 2.0},
        "2": {"id": 2, "started_at": 200, "cost": 3.0},
    }
    incoming = [
        {"id": 2, "started_at": 200, "cost": 4.5},
        {"id": 3, "started_at": 300, "cost": 1.5},
    ]
    merged = life.merge_records(existing, incoming, life.compact_charge, replace=False)
    assert len(merged) == 3
    assert merged["2"]["cost"] == 4.5
    assert merged["3"]["cost"] == 1.5


def test_full_refresh_replaces_old_records():
    existing = {"1": {"id": 1, "started_at": 100, "cost": 2.0}}
    merged = life.merge_records(
        existing,
        [{"id": 2, "started_at": 200, "cost": 3.0}],
        life.compact_charge,
        replace=True,
    )
    assert set(merged) == {"2"}


def test_lifetime_math_helpers():
    records = [
        {"id": 1, "started_at": 100, "energy_added": 10, "cost": 2.5},
        {"id": 2, "started_at": 200, "energy_added": 20, "cost": None},
    ]
    assert life.earliest_timestamp(records) == 100
    assert life.optional_sum(records, "energy_added") == 30
    assert life.optional_sum(records, "missing") is None
    assert life.percent(75, 100) == 75


def test_battery_measurement_delta():
    records = [
        {"timestamp": 100, "capacity": 75.0, "max_range": 300},
        {"timestamp": 200, "capacity": 73.5, "max_range": 294},
    ]
    assert life.earliest_measurement(records)["capacity"] == 75.0
    assert life.measurement_delta(records, "capacity") == -1.5
    assert life.measurement_delta(records, "max_range") == -6
