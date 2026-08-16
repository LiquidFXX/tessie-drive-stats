"""Pure calculation helpers for Tessie Drive Stats."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def _number(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def optional_number(value: Any) -> float | None:
    """Return a numeric API value, preserving missing/null as None."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    return False


def latest_record(records: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    records = list(records)
    if not records:
        return None
    return max(records, key=lambda item: _number(item.get("ended_at") or item.get("timestamp")))


def records_since(
    records: Iterable[dict[str, Any]],
    start_timestamp: int,
) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if _number(record.get("started_at") or record.get("timestamp")) >= start_timestamp
    ]


def drive_count(drives: list[dict[str, Any]]) -> int:
    return len(drives)


def drive_miles(drives: list[dict[str, Any]]) -> float:
    return round(sum(_number(d.get("odometer_distance")) for d in drives), 2)


def drive_energy(drives: list[dict[str, Any]]) -> float:
    return round(sum(_number(d.get("energy_used")) for d in drives), 2)


def drive_time_minutes(drives: list[dict[str, Any]]) -> float:
    seconds = sum(
        max(0.0, _number(d.get("ended_at")) - _number(d.get("started_at")))
        for d in drives
    )
    return round(seconds / 60, 1)


def drive_efficiency(drives: list[dict[str, Any]]) -> float:
    miles = drive_miles(drives)
    energy = drive_energy(drives)
    if miles <= 0:
        return 0.0
    return round((energy * 1000) / miles)


def drive_battery_used(drives: list[dict[str, Any]]) -> float:
    return round(
        sum(
            _number(d.get("starting_battery")) - _number(d.get("ending_battery"))
            for d in drives
        )
    )


def drive_autopilot_miles(drives: list[dict[str, Any]]) -> float | None:
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


def drive_average_speed(drives: list[dict[str, Any]]) -> float | None:
    minutes = drive_time_minutes(drives)
    miles = drive_miles(drives)
    if not drives or minutes <= 0:
        return None
    return round(miles / (minutes / 60), 1)


def drive_max_speed(drives: list[dict[str, Any]]) -> float | None:
    values = [optional_number(d.get("max_speed")) for d in drives]
    values = [value for value in values if value is not None]
    return max(values) if values else None


def longest_drive(drives: list[dict[str, Any]]) -> float:
    return round(max((_number(d.get("odometer_distance")) for d in drives), default=0), 2)


def drive_sum_field(drives: list[dict[str, Any]], field: str) -> float:
    return round(sum(_number(d.get(field)) for d in drives), 2)


def drive_weighted_average(drives: list[dict[str, Any]], field: str) -> float | None:
    weighted = 0.0
    total_seconds = 0.0
    for drive in drives:
        value = optional_number(drive.get(field))
        if value is None:
            continue
        seconds = max(0.0, _number(drive.get("ended_at")) - _number(drive.get("started_at")))
        if seconds <= 0:
            seconds = 1.0
        weighted += value * seconds
        total_seconds += seconds
    return round(weighted / total_seconds, 1) if total_seconds else None


def record_distance(record: dict[str, Any] | None) -> float | None:
    if not record:
        return None
    return round(_number(record.get("odometer_distance")), 2)


def record_autopilot_distance(record: dict[str, Any] | None) -> float | None:
    if not record or record.get("autopilot_distance") is None:
        return None
    return round(_number(record.get("autopilot_distance")), 2)


def record_energy(record: dict[str, Any] | None) -> float | None:
    if not record:
        return None
    return round(_number(record.get("energy_used")), 2)


def record_time_minutes(record: dict[str, Any] | None) -> float | None:
    if not record:
        return None
    seconds = max(0.0, _number(record.get("ended_at")) - _number(record.get("started_at")))
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
    return round(_number(record.get("starting_battery")) - _number(record.get("ending_battery")))


def record_location(record: dict[str, Any] | None, *, ending: bool) -> str | None:
    if not record:
        return None
    prefix = "ending" if ending else "starting"
    return record.get(f"{prefix}_saved_location") or record.get(f"{prefix}_location")


def cost_since(charges: list[dict[str, Any]], start_timestamp: int) -> float:
    return round(
        sum(
            _number(charge.get("cost"))
            for charge in charges
            if _number(charge.get("started_at")) >= start_timestamp
        ),
        2,
    )


def supercharger_records(charges: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [charge for charge in charges if _truthy(charge.get("is_supercharger"))]


def supercharger_count_since(charges: list[dict[str, Any]], start_timestamp: int) -> int:
    return len(records_since(supercharger_records(charges), start_timestamp))


def supercharger_energy_since(charges: list[dict[str, Any]], start_timestamp: int) -> float:
    return round(
        sum(
            _number(charge.get("energy_added"))
            for charge in supercharger_records(charges)
            if _number(charge.get("started_at")) >= start_timestamp
        ),
        2,
    )


def supercharger_cost_since(charges: list[dict[str, Any]], start_timestamp: int) -> float:
    return round(
        sum(
            _number(charge.get("cost"))
            for charge in supercharger_records(charges)
            if _number(charge.get("started_at")) >= start_timestamp
        ),
        2,
    )


# Idle / parked-drain helpers

def idle_count(idles: list[dict[str, Any]]) -> int:
    return len(idles)


def idle_time_minutes(idles: list[dict[str, Any]]) -> float:
    seconds = sum(
        max(0.0, _number(i.get("ended_at")) - _number(i.get("started_at")))
        for i in idles
    )
    return round(seconds / 60, 1)


def idle_energy(idles: list[dict[str, Any]]) -> float:
    return round(sum(_number(i.get("energy_used")) for i in idles), 2)


def idle_battery_used(idles: list[dict[str, Any]]) -> float:
    return round(
        sum(max(0.0, _number(i.get("starting_battery")) - _number(i.get("ending_battery"))) for i in idles),
        1,
    )


def idle_rated_range_used(idles: list[dict[str, Any]]) -> float:
    return round(sum(_number(i.get("rated_range_used")) for i in idles), 2)


def idle_fraction_time_minutes(idles: list[dict[str, Any]], field: str) -> float:
    seconds = 0.0
    for idle in idles:
        duration = max(0.0, _number(idle.get("ended_at")) - _number(idle.get("started_at")))
        fraction = min(1.0, max(0.0, _number(idle.get(field))))
        seconds += duration * fraction
    return round(seconds / 60, 1)


def record_idle_fraction_percent(record: dict[str, Any] | None, field: str) -> float | None:
    if not record or record.get(field) is None:
        return None
    return round(min(1.0, max(0.0, _number(record.get(field)))) * 100, 1)


# Consumption since charge

def consumption_non_driving(data: dict[str, Any], total_field: str, driving_field: str) -> float | None:
    total = optional_number(data.get(total_field))
    driving = optional_number(data.get(driving_field))
    if total is None or driving is None:
        return None
    return round(total - driving, 2)


def consumption_driving_share(data: dict[str, Any]) -> float | None:
    total = optional_number(data.get("energy_used"))
    driving = optional_number(data.get("energy_used_by_driving"))
    if total is None or driving is None or total <= 0:
        return None
    return round((driving / total) * 100, 1)


# Battery health history
def measurement_change(records: list[dict[str, Any]], field: str) -> float | None:
    ordered = sorted(
        records,
        key=lambda record: _number(record.get("timestamp")),
    )
    values = [optional_number(record.get(field)) for record in ordered]
    values = [value for value in values if value is not None]
    if len(values) < 2:
        return None
    return round(values[-1] - values[0], 2)


def measurements_since(records: list[dict[str, Any]], start_timestamp: int) -> list[dict[str, Any]]:
    timestamped = [r for r in records if optional_number(r.get("timestamp")) is not None]
    if not timestamped:
        return records
    return [r for r in timestamped if _number(r.get("timestamp")) >= start_timestamp]


# Historical activity helpers
def activity_summary(states: list[dict[str, Any]], start_timestamp: int, end_timestamp: int) -> dict[str, float | int]:
    """Best-effort duration summary from Tessie historical state samples."""
    ordered = sorted(
        (s for s in states if optional_number(s.get("timestamp")) is not None),
        key=lambda s: _number(s.get("timestamp")),
    )
    totals = {"awake": 0.0, "asleep": 0.0, "waiting_for_sleep": 0.0}
    wakeups = 0
    previous_normalized: str | None = None

    def normalize(value: Any) -> str | None:
        text = str(value or "").strip().lower()
        if text in {"online", "awake"}:
            return "awake"
        if text == "asleep":
            return "asleep"
        if text == "waiting_for_sleep":
            return "waiting_for_sleep"
        return None

    for index, sample in enumerate(ordered):
        ts = max(start_timestamp, int(_number(sample.get("timestamp"))))
        next_ts = (
            min(end_timestamp, int(_number(ordered[index + 1].get("timestamp"))))
            if index + 1 < len(ordered)
            else end_timestamp
        )
        current = normalize(sample.get("state"))
        if current and next_ts > ts:
            totals[current] += next_ts - ts
        if current == "awake" and previous_normalized in {"asleep", "waiting_for_sleep"}:
            wakeups += 1
        if current is not None:
            previous_normalized = current

    return {
        "awake_minutes": round(totals["awake"] / 60, 1),
        "asleep_minutes": round(totals["asleep"] / 60, 1),
        "waiting_for_sleep_minutes": round(totals["waiting_for_sleep"] / 60, 1),
        "wakeups": wakeups,
    }


# Driving path helpers
def path_autopilot_active(point: dict[str, Any]) -> bool:
    status = str(point.get("autopilot") or "").strip().lower()
    return bool(status) and status not in {"off", "standby", "unavailable", "none", "false"}


def path_autopilot_share(points: list[dict[str, Any]]) -> float | None:
    detailed = [p for p in points if p.get("autopilot") is not None]
    if not detailed:
        return None
    active = sum(1 for point in detailed if path_autopilot_active(point))
    return round(active / len(detailed) * 100, 1)


def simplify_path(points: list[dict[str, Any]], max_points: int = 200) -> list[dict[str, Any]]:
    """Return recorder-friendly route attributes with at most max_points points."""
    if not points:
        return []
    step = max(1, (len(points) + max_points - 1) // max_points)
    selected = points[::step]
    if selected[-1] is not points[-1]:
        selected.append(points[-1])
    return [
        {
            key: point.get(key)
            for key in ("timestamp", "latitude", "longitude", "heading", "battery_level", "speed", "odometer", "autopilot")
            if point.get(key) is not None
        }
        for point in selected[:max_points]
    ]


# Fleet invoice helpers
def invoice_records_for_vin(records: Iterable[dict[str, Any]], vin: str) -> list[dict[str, Any]]:
    return [r for r in records if str(r.get("vin", "")).upper() == vin.upper()]


def invoice_sum(records: Iterable[dict[str, Any]], field: str) -> float:
    return round(sum(_number(r.get(field)) for r in records), 2)
