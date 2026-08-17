"""Helpers for privacy-minimized lifetime Tessie history caching."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Callable


def optional_number(value: Any) -> float | None:
    """Return a number while preserving missing values."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def record_key(record: dict[str, Any]) -> str:
    """Return a stable key for a historical Tessie record."""
    record_id = record.get("id")
    if record_id is not None:
        return str(record_id)

    started = record.get("started_at") or record.get("timestamp") or 0
    ended = record.get("ended_at") or 0
    return f"{started}:{ended}"


def _compact(record: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    """Keep only fields needed for lifetime math; omit location and GPS data."""
    compacted = {field: record.get(field) for field in fields if record.get(field) is not None}
    if "id" in record and record.get("id") is not None:
        compacted["id"] = record.get("id")
    return compacted


def compact_drive(record: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        record,
        (
            "id",
            "started_at",
            "ended_at",
            "odometer_distance",
            "energy_used",
            "autopilot_distance",
            "average_speed",
            "max_speed",
            "rated_range_used",
            "average_inside_temperature",
            "average_outside_temperature",
        ),
    )


def compact_charge(record: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        record,
        (
            "id",
            "started_at",
            "ended_at",
            "energy_added",
            "energy_used",
            "cost",
            "is_supercharger",
        ),
    )


def compact_idle(record: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        record,
        (
            "id",
            "started_at",
            "ended_at",
            "starting_battery",
            "ending_battery",
            "rated_range_used",
            "climate_fraction",
            "sentry_fraction",
            "energy_used",
        ),
    )


def compact_battery_health(record: dict[str, Any]) -> dict[str, Any]:
    return _compact(
        record,
        (
            "timestamp",
            "capacity",
            "max_range",
            "max_ideal_range",
        ),
    )


def merge_records(
    existing: dict[str, dict[str, Any]],
    records: Iterable[dict[str, Any]],
    compactor: Callable[[dict[str, Any]], dict[str, Any]],
    *,
    replace: bool,
) -> dict[str, dict[str, Any]]:
    """Merge historical records by stable record identity."""
    merged: dict[str, dict[str, Any]] = {} if replace else dict(existing)
    for record in records:
        compacted = compactor(record)
        merged[record_key(compacted)] = compacted
    return merged


def earliest_timestamp(records: Iterable[dict[str, Any]]) -> int | None:
    """Return the oldest started_at/timestamp in a record collection."""
    timestamps: list[int] = []
    for record in records:
        value = optional_number(record.get("started_at") or record.get("timestamp"))
        if value is not None and value > 0:
            timestamps.append(int(value))
    return min(timestamps) if timestamps else None


def optional_sum(records: Iterable[dict[str, Any]], field: str) -> float | None:
    """Sum a field only when Tessie provided at least one value."""
    values = [optional_number(record.get(field)) for record in records]
    values = [value for value in values if value is not None]
    return round(sum(values), 2) if values else None


def percent(numerator: float | None, denominator: float | None) -> float | None:
    """Return a percentage when both values are usable."""
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 1)


def earliest_measurement(records: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the oldest timestamped battery-health measurement."""
    timestamped = [
        record
        for record in records
        if optional_number(record.get("timestamp")) is not None
    ]
    if not timestamped:
        return None
    return min(timestamped, key=lambda record: float(record.get("timestamp") or 0))


def latest_measurement(records: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the newest timestamped battery-health measurement."""
    timestamped = [
        record
        for record in records
        if optional_number(record.get("timestamp")) is not None
    ]
    if not timestamped:
        return None
    return max(timestamped, key=lambda record: float(record.get("timestamp") or 0))


def measurement_delta(records: Iterable[dict[str, Any]], field: str) -> float | None:
    """Return newest minus oldest battery-health measurement."""
    oldest = earliest_measurement(records)
    newest = latest_measurement(records)
    if oldest is None or newest is None:
        return None
    start = optional_number(oldest.get(field))
    end = optional_number(newest.get(field))
    if start is None or end is None:
        return None
    return round(end - start, 2)
