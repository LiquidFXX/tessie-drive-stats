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


def _truthy(value: Any) -> bool:
    """Return whether an API value represents true."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    return False


def latest_record(records: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the record with the greatest ended_at timestamp."""
    records = list(records)
    if not records:
        return None
    return max(records, key=lambda item: _number(item.get("ended_at")))


def records_since(
    records: Iterable[dict[str, Any]],
    start_timestamp: int,
) -> list[dict[str, Any]]:
    """Return records beginning at or after a Unix timestamp."""
    return [
        record
        for record in records
        if _number(record.get("started_at")) >= start_timestamp
    ]


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


def drive_autopilot_miles(drives: list[dict[str, Any]]) -> float | None:
    """Return combined Autopilot/FSD distance reported by Tessie."""
    if not drives:
        return 0.0

    values = [
        drive.get("autopilot_distance")
        for drive in drives
        if drive.get("autopilot_distance") is not None
    ]
    if not values:
        return None

    return round(sum(_number(value) for value in values), 2)


def record_distance(record: dict[str, Any] | None) -> float | None:
    """Return a drive's distance."""
    if not record:
        return None
    return round(_number(record.get("odometer_distance")), 2)


def record_autopilot_distance(record: dict[str, Any] | None) -> float | None:
    """Return a drive's combined Autopilot/FSD distance when reported."""
    if not record or record.get("autopilot_distance") is None:
        return None
    return round(_number(record.get("autopilot_distance")), 2)


def record_energy(record: dict[str, Any] | None) -> float | None:
    """Return a drive's energy used."""
    if not record:
        return None
    return round(_number(record.get("energy_used")), 2)


def record_time_minutes(record: dict[str, Any] | None) -> float | None:
    """Return a record duration in minutes."""
    if not record:
        return None
    seconds = max(
        0.0,
        _number(record.get("ended_at")) - _number(record.get("started_at")),
    )
    return round(seconds / 60, 1)


def record_efficiency(record: dict[str, Any] | None) -> float | None:
    """Return a drive's efficiency in Wh/mi."""
    if not record:
        return None
    miles = _number(record.get("odometer_distance"))
    energy = _number(record.get("energy_used"))
    if miles <= 0:
        return 0.0
    return round((energy * 1000) / miles)


def record_battery_used(record: dict[str, Any] | None) -> float | None:
    """Return battery percentage used during a drive."""
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


def supercharger_records(
    charges: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return only Tessie records identified as Supercharger sessions."""
    return [charge for charge in charges if _truthy(charge.get("is_supercharger"))]


def supercharger_count_since(
    charges: list[dict[str, Any]],
    start_timestamp: int,
) -> int:
    """Return Supercharger session count since a boundary."""
    return len(records_since(supercharger_records(charges), start_timestamp))


def supercharger_energy_since(
    charges: list[dict[str, Any]],
    start_timestamp: int,
) -> float:
    """Return Supercharger energy added since a boundary in kWh."""
    total = sum(
        _number(charge.get("energy_added"))
        for charge in supercharger_records(charges)
        if _number(charge.get("started_at")) >= start_timestamp
    )
    return round(total, 2)


def supercharger_cost_since(
    charges: list[dict[str, Any]],
    start_timestamp: int,
) -> float:
    """Return Supercharger cost since a boundary."""
    total = sum(
        _number(charge.get("cost"))
        for charge in supercharger_records(charges)
        if _number(charge.get("started_at")) >= start_timestamp
    )
    return round(total, 2)
