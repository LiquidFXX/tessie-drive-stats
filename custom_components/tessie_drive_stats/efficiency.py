"""Pure efficiency-intelligence helpers for Tessie Drive Stats."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

SECONDS_PER_DAY = 86400
COMPARISON_DAYS = 30
SIMILAR_TEMPERATURE_TOLERANCE_F = 7.5
SIMILAR_SPEED_TOLERANCE_MPH = 7.5
MIN_COMPARISON_DRIVES = 3
MIN_ALERT_DRIVES = 5
UNUSUAL_EFFICIENCY_THRESHOLD_PERCENT = 20.0

TEMPERATURE_BANDS: tuple[tuple[str, float | None, float | None], ...] = (
    ("below_40_f", None, 40.0),
    ("40_to_60_f", 40.0, 60.0),
    ("60_to_75_f", 60.0, 75.0),
    ("75_to_90_f", 75.0, 90.0),
    ("90_f_and_above", 90.0, None),
)

SPEED_BANDS: tuple[tuple[str, float | None, float | None], ...] = (
    ("low_speed_below_25_mph", None, 25.0),
    ("mixed_25_to_45_mph", 25.0, 45.0),
    ("highway_45_mph_and_above", 45.0, None),
)


def optional_number(value: Any) -> float | None:
    """Return a numeric value while preserving missing data."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _record_identity(record: dict[str, Any] | None) -> tuple[Any, Any, Any] | None:
    if not record:
        return None
    return (
        record.get("id"),
        record.get("started_at"),
        record.get("ended_at"),
    )


def exclude_drive(
    drives: Iterable[dict[str, Any]],
    target: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Exclude the target drive from a historical comparison set."""
    target_identity = _record_identity(target)
    if target_identity is None:
        return list(drives)

    target_id, target_started, target_ended = target_identity
    result: list[dict[str, Any]] = []
    for drive in drives:
        drive_id, started, ended = _record_identity(drive) or (None, None, None)
        same = False
        if target_id is not None and drive_id is not None:
            same = str(target_id) == str(drive_id)
        elif target_started is not None and target_ended is not None:
            same = started == target_started and ended == target_ended
        if not same:
            result.append(drive)
    return result


def drive_efficiency_wh_per_mile(record: dict[str, Any] | None) -> float | None:
    """Return Wh/mi for one drive when distance and energy are usable."""
    if not record:
        return None
    miles = optional_number(record.get("odometer_distance"))
    energy = optional_number(record.get("energy_used"))
    if miles is None or energy is None or miles <= 0 or energy < 0:
        return None
    return round((energy * 1000.0) / miles, 1)


def usable_drives(drives: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return drives that can contribute to energy-efficiency math."""
    return [drive for drive in drives if drive_efficiency_wh_per_mile(drive) is not None]


def aggregate_efficiency(drives: Iterable[dict[str, Any]]) -> float | None:
    """Return distance-weighted Wh/mi across drives."""
    miles = 0.0
    energy = 0.0
    count = 0
    for drive in drives:
        distance = optional_number(drive.get("odometer_distance"))
        used = optional_number(drive.get("energy_used"))
        if distance is None or used is None or distance <= 0 or used < 0:
            continue
        miles += distance
        energy += used
        count += 1
    if count == 0 or miles <= 0:
        return None
    return round((energy * 1000.0) / miles, 1)


def percent_difference(value: float | None, baseline: float | None) -> float | None:
    """Return percent difference from baseline; positive means higher Wh/mi."""
    if value is None or baseline is None or baseline <= 0:
        return None
    return round(((value - baseline) / baseline) * 100.0, 1)


def recent_drives(
    drives: Iterable[dict[str, Any]],
    now_timestamp: int,
    *,
    days: int = COMPARISON_DAYS,
) -> list[dict[str, Any]]:
    """Return drives starting within the requested rolling window."""
    threshold = now_timestamp - (days * SECONDS_PER_DAY)
    return [
        drive
        for drive in drives
        if (optional_number(drive.get("started_at")) or 0) >= threshold
    ]


def similar_temperature_drives(
    drives: Iterable[dict[str, Any]],
    target_temperature: float | None,
    *,
    tolerance: float = SIMILAR_TEMPERATURE_TOLERANCE_F,
) -> list[dict[str, Any]]:
    """Return drives within a Fahrenheit temperature tolerance."""
    if target_temperature is None:
        return []
    result = []
    for drive in drives:
        value = optional_number(drive.get("average_outside_temperature"))
        if value is not None and abs(value - target_temperature) <= tolerance:
            result.append(drive)
    return result


def similar_speed_drives(
    drives: Iterable[dict[str, Any]],
    target_speed: float | None,
    *,
    tolerance: float = SIMILAR_SPEED_TOLERANCE_MPH,
) -> list[dict[str, Any]]:
    """Return drives within an average-speed tolerance."""
    if target_speed is None:
        return []
    result = []
    for drive in drives:
        value = optional_number(drive.get("average_speed"))
        if value is not None and abs(value - target_speed) <= tolerance:
            result.append(drive)
    return result


def band_for_value(
    value: float | None,
    bands: tuple[tuple[str, float | None, float | None], ...],
) -> str | None:
    """Return the configured half-open band containing value."""
    if value is None:
        return None
    for name, minimum, maximum in bands:
        if minimum is not None and value < minimum:
            continue
        if maximum is not None and value >= maximum:
            continue
        return name
    return None


def temperature_band(value: float | None) -> str | None:
    return band_for_value(value, TEMPERATURE_BANDS)


def speed_band(value: float | None) -> str | None:
    return band_for_value(value, SPEED_BANDS)


def drives_in_band(
    drives: Iterable[dict[str, Any]],
    *,
    field: str,
    band_name: str | None,
    bands: tuple[tuple[str, float | None, float | None], ...],
) -> list[dict[str, Any]]:
    """Return drives whose field falls in one named band."""
    if band_name is None:
        return []
    return [
        drive
        for drive in drives
        if band_for_value(optional_number(drive.get(field)), bands) == band_name
    ]


def band_efficiency_summary(
    drives: Iterable[dict[str, Any]],
    *,
    field: str,
    bands: tuple[tuple[str, float | None, float | None], ...],
    minimum_drives: int = MIN_COMPARISON_DRIVES,
) -> dict[str, dict[str, float | int]]:
    """Return count and weighted efficiency for sufficiently populated bands."""
    records = list(drives)
    summary: dict[str, dict[str, float | int]] = {}
    for band_name, _, _ in bands:
        group = drives_in_band(records, field=field, band_name=band_name, bands=bands)
        group = usable_drives(group)
        if len(group) < minimum_drives:
            continue
        efficiency = aggregate_efficiency(group)
        if efficiency is None:
            continue
        summary[band_name] = {"drives": len(group), "efficiency": efficiency}
    return summary


def best_worst_band(
    drives: Iterable[dict[str, Any]],
    *,
    field: str,
    bands: tuple[tuple[str, float | None, float | None], ...],
    minimum_drives: int = MIN_COMPARISON_DRIVES,
) -> tuple[tuple[str, float] | None, tuple[str, float] | None]:
    """Return best (lowest Wh/mi) and worst bands."""
    summary = band_efficiency_summary(
        drives,
        field=field,
        bands=bands,
        minimum_drives=minimum_drives,
    )
    if not summary:
        return None, None
    ranked = sorted(
        ((name, float(values["efficiency"])) for name, values in summary.items()),
        key=lambda item: item[1],
    )
    return ranked[0], ranked[-1]


def efficiency_percentile(
    target_efficiency: float | None,
    drives: Iterable[dict[str, Any]],
) -> float | None:
    """Return energy-intensity percentile; 100 means among highest Wh/mi."""
    if target_efficiency is None:
        return None
    efficiencies = [
        efficiency
        for drive in drives
        if (efficiency := drive_efficiency_wh_per_mile(drive)) is not None
    ]
    if len(efficiencies) < MIN_COMPARISON_DRIVES:
        return None
    lower_or_equal = sum(1 for efficiency in efficiencies if efficiency <= target_efficiency)
    return round((lower_or_equal / len(efficiencies)) * 100.0, 1)


def efficiency_context(percent_vs_30_day: float | None) -> str:
    """Return a non-causal label describing last-drive Wh/mi vs recent baseline."""
    if percent_vs_30_day is None:
        return "insufficient_data"
    if percent_vs_30_day <= -15:
        return "much_better_than_typical"
    if percent_vs_30_day <= -5:
        return "better_than_typical"
    if percent_vs_30_day < 5:
        return "typical"
    if percent_vs_30_day < 15:
        return "higher_than_typical"
    return "much_higher_than_typical"


def efficiency_intelligence(data: dict[str, Any]) -> dict[str, Any]:
    """Build all v0.5 last-drive efficiency context in one pure calculation."""
    target = data.get("last_drive")
    now_timestamp = int((data.get("boundaries") or {}).get("now") or 0)
    history = exclude_drive(data.get("lifetime_drives", []), target)
    history = usable_drives(history)

    last_efficiency = drive_efficiency_wh_per_mile(target)
    last_outside = optional_number((target or {}).get("average_outside_temperature"))
    last_inside = optional_number((target or {}).get("average_inside_temperature"))
    last_speed = optional_number((target or {}).get("average_speed"))

    recent = usable_drives(recent_drives(history, now_timestamp)) if now_timestamp else []
    recent_eff = aggregate_efficiency(recent) if len(recent) >= MIN_COMPARISON_DRIVES else None

    temp_matches = usable_drives(similar_temperature_drives(history, last_outside))
    temp_eff = aggregate_efficiency(temp_matches) if len(temp_matches) >= MIN_COMPARISON_DRIVES else None

    speed_matches = usable_drives(similar_speed_drives(history, last_speed))
    speed_eff = aggregate_efficiency(speed_matches) if len(speed_matches) >= MIN_COMPARISON_DRIVES else None

    temp_band_name = temperature_band(last_outside)
    temp_band_drives = usable_drives(
        drives_in_band(
            history,
            field="average_outside_temperature",
            band_name=temp_band_name,
            bands=TEMPERATURE_BANDS,
        )
    )
    temp_band_eff = (
        aggregate_efficiency(temp_band_drives)
        if len(temp_band_drives) >= MIN_COMPARISON_DRIVES
        else None
    )

    speed_band_name = speed_band(last_speed)
    speed_band_drives = usable_drives(
        drives_in_band(
            history,
            field="average_speed",
            band_name=speed_band_name,
            bands=SPEED_BANDS,
        )
    )
    speed_band_eff = (
        aggregate_efficiency(speed_band_drives)
        if len(speed_band_drives) >= MIN_COMPARISON_DRIVES
        else None
    )

    best_temp, worst_temp = best_worst_band(
        history,
        field="average_outside_temperature",
        bands=TEMPERATURE_BANDS,
    )
    best_speed, worst_speed = best_worst_band(
        history,
        field="average_speed",
        bands=SPEED_BANDS,
    )

    vs_30 = percent_difference(last_efficiency, recent_eff)

    return {
        "last_efficiency": last_efficiency,
        "recent_30_day_efficiency": recent_eff,
        "recent_30_day_drives": len(recent),
        "vs_30_day_percent": vs_30,
        "similar_temperature_efficiency": temp_eff,
        "similar_temperature_drives": len(temp_matches),
        "vs_similar_temperature_percent": percent_difference(last_efficiency, temp_eff),
        "similar_speed_efficiency": speed_eff,
        "similar_speed_drives": len(speed_matches),
        "vs_similar_speed_percent": percent_difference(last_efficiency, speed_eff),
        "efficiency_percentile": efficiency_percentile(last_efficiency, history),
        "temperature_band": temp_band_name,
        "temperature_band_efficiency": temp_band_eff,
        "temperature_band_drives": len(temp_band_drives),
        "best_temperature_band": best_temp[0] if best_temp else None,
        "best_temperature_band_efficiency": best_temp[1] if best_temp else None,
        "worst_temperature_band": worst_temp[0] if worst_temp else None,
        "worst_temperature_band_efficiency": worst_temp[1] if worst_temp else None,
        "speed_band": speed_band_name,
        "speed_band_efficiency": speed_band_eff,
        "speed_band_drives": len(speed_band_drives),
        "best_speed_band": best_speed[0] if best_speed else None,
        "best_speed_band_efficiency": best_speed[1] if best_speed else None,
        "worst_speed_band": worst_speed[0] if worst_speed else None,
        "worst_speed_band_efficiency": worst_speed[1] if worst_speed else None,
        "cabin_outside_temperature_delta": (
            round(abs(last_inside - last_outside), 1)
            if last_inside is not None and last_outside is not None
            else None
        ),
        "context": efficiency_context(vs_30),
        "unusually_inefficient": (
            len(recent) >= MIN_ALERT_DRIVES
            and vs_30 is not None
            and vs_30 >= UNUSUAL_EFFICIENCY_THRESHOLD_PERCENT
        ),
    }
