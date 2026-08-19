"""Pure charging-economics helpers for Tessie Drive Stats."""

from __future__ import annotations

from typing import Any, Iterable


def optional_number(value: Any) -> float | None:
    """Return a numeric value while preserving missing data."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def record_timestamp(record: dict[str, Any]) -> float | None:
    """Return the primary timestamp for a historical record."""
    return optional_number(record.get("started_at") or record.get("timestamp"))


def records_between(
    records: Iterable[dict[str, Any]],
    start: int,
    end: int | None = None,
) -> list[dict[str, Any]]:
    """Filter records to [start, end)."""
    selected: list[dict[str, Any]] = []
    for record in records:
        timestamp = record_timestamp(record)
        if timestamp is None or timestamp < start:
            continue
        if end is not None and timestamp >= end:
            continue
        selected.append(record)
    return selected


def charge_cost(charges: Iterable[dict[str, Any]]) -> float | None:
    """Sum recorded charge cost when Tessie supplied at least one cost."""
    values = [optional_number(charge.get("cost")) for charge in charges]
    values = [value for value in values if value is not None]
    return round(sum(values), 2) if values else None


def charge_energy_used(charges: Iterable[dict[str, Any]]) -> float | None:
    """Sum charger-side energy used when available."""
    values = [optional_number(charge.get("energy_used")) for charge in charges]
    values = [value for value in values if value is not None]
    return round(sum(values), 3) if values else None


def charging_efficiency(charges: Iterable[dict[str, Any]]) -> float | None:
    """Return aggregate battery-added / charger-used energy percentage.

    Tessie defines charging efficiency as energy added to the battery divided by
    energy used by the charger. Only sessions containing both measurements are
    included, preventing partial records from skewing the result.
    """
    added = 0.0
    used = 0.0
    samples = 0
    for charge in charges:
        energy_added = optional_number(charge.get("energy_added"))
        energy_used = optional_number(charge.get("energy_used"))
        if energy_added is None or energy_used is None or energy_used <= 0:
            continue
        if energy_added < 0:
            continue
        added += energy_added
        used += energy_used
        samples += 1
    if samples == 0 or used <= 0:
        return None
    return round((added / used) * 100, 1)


def charging_loss(charges: Iterable[dict[str, Any]]) -> float | None:
    """Return 100 - charging efficiency without hiding measurement variance."""
    efficiency = charging_efficiency(charges)
    return round(100 - efficiency, 1) if efficiency is not None else None


def average_charging_cost_per_kwh(
    charges: Iterable[dict[str, Any]],
) -> float | None:
    """Return energy-weighted recorded cost per charger-side kWh.

    Only sessions with both a recorded cost and positive charger-side energy are
    used. This avoids treating a missing cost as free charging.
    """
    total_cost = 0.0
    total_energy = 0.0
    samples = 0
    for charge in charges:
        cost = optional_number(charge.get("cost"))
        energy_used = optional_number(charge.get("energy_used"))
        if cost is None or energy_used is None or energy_used <= 0:
            continue
        total_cost += cost
        total_energy += energy_used
        samples += 1
    if samples == 0 or total_energy <= 0:
        return None
    return round(total_cost / total_energy, 4)


def charging_cost_coverage(charges: Iterable[dict[str, Any]]) -> float | None:
    """Return charger-energy share belonging to sessions with a recorded cost."""
    total_energy = 0.0
    covered_energy = 0.0
    for charge in charges:
        energy_used = optional_number(charge.get("energy_used"))
        if energy_used is None or energy_used <= 0:
            continue
        total_energy += energy_used
        if optional_number(charge.get("cost")) is not None:
            covered_energy += energy_used
    if total_energy <= 0:
        return None
    return round((covered_energy / total_energy) * 100, 1)


def record_charging_efficiency(charge: dict[str, Any] | None) -> float | None:
    """Return charging efficiency for one session."""
    return charging_efficiency([charge]) if charge else None


def record_charging_loss(charge: dict[str, Any] | None) -> float | None:
    """Return charging loss for one session."""
    return charging_loss([charge]) if charge else None


def record_cost_per_kwh(charge: dict[str, Any] | None) -> float | None:
    """Return cost per charger-side kWh for one session."""
    return average_charging_cost_per_kwh([charge]) if charge else None


def drive_energy(drives: Iterable[dict[str, Any]]) -> float | None:
    """Sum drive energy only when at least one drive reports energy."""
    values = [optional_number(drive.get("energy_used")) for drive in drives]
    values = [value for value in values if value is not None]
    return round(sum(values), 3) if values else None


def drive_distance(drives: Iterable[dict[str, Any]]) -> float | None:
    """Sum drive distance only when at least one drive reports distance."""
    values = [optional_number(drive.get("odometer_distance")) for drive in drives]
    values = [value for value in values if value is not None]
    return round(sum(values), 3) if values else None


def estimated_driving_cost(
    drives: Iterable[dict[str, Any]],
    average_cost_per_kwh: float | None,
) -> float | None:
    """Estimate driving cost from drive energy and average charging price."""
    energy = drive_energy(drives)
    if energy is None or average_cost_per_kwh is None:
        return None
    return round(energy * average_cost_per_kwh, 2)


def estimated_drive_cost_per_mile(
    drives: Iterable[dict[str, Any]],
    average_cost_per_kwh: float | None,
) -> float | None:
    """Estimate cost per driven mile from real drive energy usage."""
    energy = drive_energy(drives)
    distance = drive_distance(drives)
    if (
        energy is None
        or distance is None
        or distance <= 0
        or average_cost_per_kwh is None
    ):
        return None
    return round((energy * average_cost_per_kwh) / distance, 4)


def projected_cost(
    cost: float | None,
    *,
    start: int,
    now: int,
    end: int,
) -> float | None:
    """Project partial-period recorded cost across the full period."""
    if cost is None or now <= start or end <= start:
        return None
    elapsed = min(now, end) - start
    total = end - start
    if elapsed <= 0:
        return None
    return round(cost * (total / elapsed), 2)


def percent_change(current: float | None, baseline: float | None) -> float | None:
    """Return percentage change from baseline."""
    if current is None or baseline is None or baseline == 0:
        return None
    return round(((current - baseline) / baseline) * 100, 1)


def supercharger_state(charge: dict[str, Any]) -> bool | None:
    """Return explicit Tessie Supercharger classification, preserving unknown."""
    value = charge.get("is_supercharger")
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "on"}:
            return True
        if text in {"false", "0", "no", "off"}:
            return False
    return None


def classified_charges(
    charges: Iterable[dict[str, Any]], *, supercharger: bool
) -> list[dict[str, Any]]:
    """Return only sessions explicitly classified by Tessie."""
    return [
        charge
        for charge in charges
        if supercharger_state(charge) is supercharger
    ]


def earliest_timestamp(records: Iterable[dict[str, Any]]) -> int | None:
    """Return earliest usable historical record timestamp."""
    values = [record_timestamp(record) for record in records]
    values = [int(value) for value in values if value is not None and value > 0]
    return min(values) if values else None


def common_coverage_start(
    charges: Iterable[dict[str, Any]], drives: Iterable[dict[str, Any]]
) -> int | None:
    """Return the first timestamp where charging and driving histories overlap."""
    charging_start = earliest_timestamp(charges)
    driving_start = earliest_timestamp(drives)
    if charging_start is None or driving_start is None:
        return None
    return max(charging_start, driving_start)


def _period_metrics(
    charges: list[dict[str, Any]], drives: list[dict[str, Any]]
) -> dict[str, Any]:
    rate = average_charging_cost_per_kwh(charges)
    return {
        "charging_efficiency": charging_efficiency(charges),
        "charging_loss": charging_loss(charges),
        "average_charging_cost_per_kwh": rate,
        "charging_cost_coverage": charging_cost_coverage(charges),
        "estimated_drive_cost_per_mile": estimated_drive_cost_per_mile(drives, rate),
        "estimated_driving_cost": estimated_driving_cost(drives, rate),
    }


def charging_economics(data: dict[str, Any]) -> dict[str, Any]:
    """Build v0.6 Charging Economics from coordinator data."""
    boundaries = data.get("boundaries") or {}
    charges_ytd = data.get("charges_ytd") or []
    drives_ytd = data.get("drives_ytd") or []
    lifetime_charges = data.get("lifetime_charges") or []
    lifetime_drives = data.get("lifetime_drives") or []

    result: dict[str, Any] = {
        "last_charge_efficiency": record_charging_efficiency(data.get("last_charge")),
        "last_charge_loss": record_charging_loss(data.get("last_charge")),
        "last_charge_cost_per_kwh": record_cost_per_kwh(data.get("last_charge")),
        "last_supercharger_cost_per_kwh": record_cost_per_kwh(
            data.get("last_supercharger")
        ),
    }

    for boundary, suffix in (
        ("today", "today"),
        ("week", "this_week"),
        ("month", "this_month"),
        ("year", "this_year"),
    ):
        start = int(boundaries.get(boundary) or 0)
        period_charges = records_between(charges_ytd, start) if start else []
        period_drives = records_between(drives_ytd, start) if start else []
        metrics = _period_metrics(period_charges, period_drives)
        for key, value in metrics.items():
            result[f"{key}_{suffix}"] = value

    month_start = int(boundaries.get("month") or 0)
    previous_month = int(boundaries.get("previous_month") or 0)
    next_month = int(boundaries.get("next_month") or 0)
    year_start = int(boundaries.get("year") or 0)
    next_year = int(boundaries.get("next_year") or 0)
    now = int(boundaries.get("now") or 0)

    current_month_charges = records_between(charges_ytd, month_start) if month_start else []
    current_month_cost = charge_cost(current_month_charges)
    last_month_charges = (
        records_between(lifetime_charges, previous_month, month_start)
        if previous_month and month_start
        else []
    )
    last_month_cost = charge_cost(last_month_charges)
    projected_month = (
        projected_cost(current_month_cost, start=month_start, now=now, end=next_month)
        if month_start and now and next_month
        else None
    )
    current_year_cost = charge_cost(
        records_between(charges_ytd, year_start) if year_start else []
    )
    projected_year = (
        projected_cost(current_year_cost, start=year_start, now=now, end=next_year)
        if year_start and now and next_year
        else None
    )

    result.update(
        {
            "charging_cost_last_month": last_month_cost,
            "projected_charging_cost_this_month": projected_month,
            "projected_charging_cost_this_year": projected_year,
            "projected_charging_cost_change_vs_last_month": percent_change(
                projected_month, last_month_cost
            ),
        }
    )

    lifetime_rate = average_charging_cost_per_kwh(lifetime_charges)
    result.update(
        {
            "recorded_lifetime_charging_efficiency": charging_efficiency(
                lifetime_charges
            ),
            "recorded_lifetime_charging_loss": charging_loss(lifetime_charges),
            "recorded_lifetime_average_charging_cost_per_kwh": lifetime_rate,
            "recorded_lifetime_charging_cost_coverage": charging_cost_coverage(
                lifetime_charges
            ),
        }
    )

    overlap_start = common_coverage_start(lifetime_charges, lifetime_drives)
    result["recorded_lifetime_economics_since"] = overlap_start
    if overlap_start is not None:
        overlapping_charges = records_between(lifetime_charges, overlap_start)
        overlapping_drives = records_between(lifetime_drives, overlap_start)
        overlapping_rate = average_charging_cost_per_kwh(overlapping_charges)
        lifetime_estimated_cost = estimated_driving_cost(
            overlapping_drives, overlapping_rate
        )
        lifetime_cost_per_mile = estimated_drive_cost_per_mile(
            overlapping_drives, overlapping_rate
        )
    else:
        lifetime_estimated_cost = None
        lifetime_cost_per_mile = None

    superchargers = classified_charges(lifetime_charges, supercharger=True)
    non_superchargers = classified_charges(lifetime_charges, supercharger=False)
    supercharger_rate = average_charging_cost_per_kwh(superchargers)
    non_supercharger_rate = average_charging_cost_per_kwh(non_superchargers)

    result.update(
        {
            "recorded_lifetime_estimated_driving_cost": lifetime_estimated_cost,
            "recorded_lifetime_estimated_drive_cost_per_mile": lifetime_cost_per_mile,
            "recorded_lifetime_non_supercharger_average_cost_per_kwh": non_supercharger_rate,
            "recorded_lifetime_supercharger_average_cost_per_kwh": supercharger_rate,
            "recorded_lifetime_supercharger_cost_premium": percent_change(
                supercharger_rate, non_supercharger_rate
            ),
        }
    )

    return result
