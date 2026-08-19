"""Tests for Tessie Drive Stats efficiency-intelligence helpers."""

import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "tessie_drive_stats"
    / "efficiency.py"
)
spec = importlib.util.spec_from_file_location("tessie_efficiency", MODULE_PATH)
eff = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(eff)

SPEED_BANDS = eff.SPEED_BANDS
TEMPERATURE_BANDS = eff.TEMPERATURE_BANDS
aggregate_efficiency = eff.aggregate_efficiency
best_worst_band = eff.best_worst_band
efficiency_context = eff.efficiency_context
efficiency_intelligence = eff.efficiency_intelligence
efficiency_percentile = eff.efficiency_percentile
percent_difference = eff.percent_difference
speed_band = eff.speed_band
temperature_band = eff.temperature_band


def drive(i, *, days_ago=10, miles=10, kwh=2.5, temp=70, speed=35):
    now = 2_000_000_000
    started = now - days_ago * 86400 - i * 10
    return {
        "id": i,
        "started_at": started,
        "ended_at": started + 1200,
        "odometer_distance": miles,
        "energy_used": kwh,
        "average_outside_temperature": temp,
        "average_inside_temperature": 72,
        "average_speed": speed,
    }


def test_weighted_efficiency():
    assert aggregate_efficiency([
        drive(1, miles=10, kwh=2),
        drive(2, miles=20, kwh=5),
    ]) == 233.3


def test_percent_difference_positive_is_worse_wh_per_mile():
    assert percent_difference(300, 250) == 20.0
    assert percent_difference(225, 250) == -10.0


def test_bands():
    assert temperature_band(39.9) == "below_40_f"
    assert temperature_band(40) == "40_to_60_f"
    assert temperature_band(90) == "90_f_and_above"
    assert speed_band(24.9) == "low_speed_below_25_mph"
    assert speed_band(25) == "mixed_25_to_45_mph"
    assert speed_band(45) == "highway_45_mph_and_above"


def test_best_worst_temperature_band_requires_samples():
    drives = [
        drive(1, temp=35, kwh=3.0), drive(2, temp=35, kwh=3.0), drive(3, temp=35, kwh=3.0),
        drive(4, temp=70, kwh=2.0), drive(5, temp=70, kwh=2.0), drive(6, temp=70, kwh=2.0),
    ]
    best, worst = best_worst_band(
        drives, field="average_outside_temperature", bands=TEMPERATURE_BANDS
    )
    assert best == ("60_to_75_f", 200.0)
    assert worst == ("below_40_f", 300.0)


def test_best_worst_speed_band():
    drives = [
        drive(1, speed=20, kwh=2.0), drive(2, speed=20, kwh=2.0), drive(3, speed=20, kwh=2.0),
        drive(4, speed=55, kwh=3.0), drive(5, speed=55, kwh=3.0), drive(6, speed=55, kwh=3.0),
    ]
    best, worst = best_worst_band(drives, field="average_speed", bands=SPEED_BANDS)
    assert best == ("low_speed_below_25_mph", 200.0)
    assert worst == ("highway_45_mph_and_above", 300.0)


def test_efficiency_percentile_high_means_more_energy_intensive():
    history = [
        drive(1, kwh=2.0), drive(2, kwh=2.5), drive(3, kwh=3.0), drive(4, kwh=3.5)
    ]
    assert efficiency_percentile(300, history) == 75.0


def test_context_labels():
    assert efficiency_context(-16) == "much_better_than_typical"
    assert efficiency_context(-7) == "better_than_typical"
    assert efficiency_context(0) == "typical"
    assert efficiency_context(8) == "higher_than_typical"
    assert efficiency_context(20) == "much_higher_than_typical"
    assert efficiency_context(None) == "insufficient_data"


def test_intelligence_excludes_last_drive_and_flags_large_30_day_delta():
    now = 2_000_000_000
    last = drive(999, days_ago=0, miles=10, kwh=3.0, temp=70, speed=35)
    history = [
        drive(1, kwh=2.0, temp=68, speed=34),
        drive(2, kwh=2.0, temp=70, speed=35),
        drive(3, kwh=2.0, temp=72, speed=36),
        drive(4, kwh=2.0, temp=69, speed=37),
        drive(5, kwh=2.0, temp=71, speed=33),
        last,
    ]
    result = efficiency_intelligence({
        "last_drive": last,
        "lifetime_drives": history,
        "boundaries": {"now": now},
    })
    assert result["recent_30_day_drives"] == 5
    assert result["recent_30_day_efficiency"] == 200.0
    assert result["vs_30_day_percent"] == 50.0
    assert result["similar_temperature_drives"] == 5
    assert result["similar_speed_drives"] == 5
    assert result["unusually_inefficient"] is True
