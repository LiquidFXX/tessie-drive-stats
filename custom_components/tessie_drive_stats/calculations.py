"""Pure calculation helpers for Tessie Drive Stats."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _number(value: Any) -> float:
    """Return a float for a possibly-null API value."""
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def latest_record(records: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the record with the greatest ended_at timestamp."""
    records = list(records)
    if not records:
        return None
    return max(records, key=lambda item: _number(item.get("ended_at")))


def drive_count(drives: list[dict[str, Any]]) -> int:
    """Return number of drives."""
    return len(drives)


def drive_miles(drives: list[dict[str, Any]]) -> float:
    """Return total miles driven."""
    return round(sum(_number(d.get("odometer_distance")) for d in drives), 2)


def drive_energy(drives: list[dict[str, Any]]) -> float:
    """Return total drive energy in kWh."""
    return round(sum(_number(d.get("energy_used")) for d in drives), 2)


def drive_time_minutes(drives: list[dict[str, Any]]) -> float:
    """Return total driving time in minutes."""
    seconds = sum(
        max(0.0, _number(d.get("ended_at")) - _number(d.get("started_at")))
        for d in drives
    )
    return round(seconds / 60, 1)


def drive_efficiency(drives: list[dict[str, Any]]) -> float:
    """Return aggregate efficiency in Wh/mi."""
    miles = sum(_number(d.get("odometer_distance")) for d in drives)
    energy = sum(_number(d.get("energy_used")) for d in drives)
    if miles <= 0:
        return 0.0
    return round((energy * 1000) / miles)


def drive_battery_used(drives: list[dict[str, Any]]) -> float:
    """Return summed battery percentage used across drives."""
    return round(
        sum(
            _number(d.get("starting_battery")) - _number(d.get("ending_battery"))
            for d in drives
        )
    )


def record_distance(record: dict[str, Any] | None) -> float | None:
    if not record:
        return None
    return round(_number(record.get("odometer_distance")), 2)


def record_energy(record: dict[str, Any] | None) -> float | None:
    if not record:
        return None
    return round(_number(record.get("energy_used")), 2)


def record_time_minutes(record: dict[str, Any] | None) -> float | None:
    if not record:
        return None
    seconds = max(
        0.0,
        _number(record.get("ended_at")) - _number(record.get("started_at")),
    )
    return round(seconds / 60, 1)


def record_efficiency(record: dict[str, Any] | None) -> float | None:
    if not record:
        return None
    miles = _number(record.get("odometer_distance"))
    energy = _number(record.get("energy_used"))
    if miles <= 0:
        return 0.0
    return round((energy * 1000) / miles)


def record_battery_used(record: dict[str, Any] | None) -> float | None:
    if not record:
        return None
    return round(
        _number(record.get("starting_battery"))
        - _number(record.get("ending_battery"))
    )


def record_location(record: dict[str, Any] | None, *, ending: bool) -> str | None:
    """Return saved location when present, otherwise the address."""
    if not record:
        return None
    prefix = "ending" if ending else "starting"
    return record.get(f"{prefix}_saved_location") or record.get(f"{prefix}_location")


def cost_since(charges: list[dict[str, Any]], start_timestamp: int) -> float:
    """Return charge cost for sessions starting at or after a boundary."""
    total = sum(
        _number(charge.get("cost"))
        for charge in charges
        if _number(charge.get("started_at")) >= start_timestamp
    )
    return round(total, 2)
