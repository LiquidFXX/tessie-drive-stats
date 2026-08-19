"""Sensor platform for Tessie Drive Stats."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfPower,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .calculations import (
    activity_summary,
    consumption_driving_share,
    consumption_non_driving,
    cost_since,
    drive_autopilot_miles,
    drive_average_speed,
    drive_battery_used,
    drive_count,
    drive_efficiency,
    drive_energy,
    drive_max_speed,
    drive_miles,
    drive_sum_field,
    drive_time_minutes,
    drive_weighted_average,
    idle_battery_used,
    idle_count,
    idle_energy,
    idle_fraction_time_minutes,
    idle_rated_range_used,
    idle_time_minutes,
    invoice_records_for_vin,
    invoice_sum,
    latest_record,
    longest_drive,
    measurement_change,
    measurements_since,
    optional_number,
    path_autopilot_share,
    record_autopilot_distance,
    record_battery_used,
    record_distance,
    record_efficiency,
    record_energy,
    record_idle_fraction_percent,
    record_location,
    record_time_minutes,
    records_since,
    simplify_path,
    supercharger_cost_since,
    supercharger_count_since,
    supercharger_energy_since,
)
from .const import CONF_VIN, DOMAIN
from .coordinator import TessieDriveStatsCoordinator

ValueFn = Callable[[dict[str, Any]], Any]
AttributesFn = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True, kw_only=True)
class TessieSensorEntityDescription(SensorEntityDescription):
    """Describe a Tessie Drive Stats sensor."""

    value_fn: ValueFn
    attributes_fn: AttributesFn | None = None
    dynamic_currency: bool = False
    invoice_currency: bool = False
    currency_suffix: str | None = None


def _timestamp(value: Any) -> datetime | None:
    number = optional_number(value)
    if number is None or number <= 0:
        return None
    return datetime.fromtimestamp(number, tz=timezone.utc)


def _nested(data: dict[str, Any], *path: str) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _period_records(data: dict[str, Any], collection: str, boundary: str) -> list[dict[str, Any]]:
    return records_since(data.get(collection, []), data["boundaries"][boundary])


def _period_drives(data: dict[str, Any], boundary: str) -> list[dict[str, Any]]:
    return _period_records(data, "drives_ytd", boundary)


def _period_idles(data: dict[str, Any], boundary: str) -> list[dict[str, Any]]:
    return _period_records(data, "idles_ytd", boundary)


def _health_value(data: dict[str, Any], key: str) -> Any:
    health = data.get("battery_health")
    return health.get(key) if isinstance(health, dict) else None


def _activity(data: dict[str, Any]) -> dict[str, float | int]:
    return activity_summary(
        data.get("historical_states_today", []),
        data["boundaries"]["today"],
        data["boundaries"]["now"],
    )


def _invoice_records(data: dict[str, Any]) -> list[dict[str, Any]]:
    records = data.get("charging_invoices")
    if not isinstance(records, list):
        return []
    # Coordinator already requests the VIN, but filter defensively in sensor memory.
    vin = str(_nested(data, "vehicle_state", "vin") or "")
    return invoice_records_for_vin(records, vin) if vin else records


def _invoice_currency(data: dict[str, Any]) -> str | None:
    records = _invoice_records(data)
    currencies = {str(r.get("currency")) for r in records if r.get("currency")}
    return next(iter(currencies)) if len(currencies) == 1 else None


def _latest_invoice(data: dict[str, Any]) -> dict[str, Any] | None:
    return latest_record(_invoice_records(data))


def _last_path_attrs(data: dict[str, Any]) -> dict[str, Any]:
    points = data.get("last_drive_path", [])
    return {
        "path": simplify_path(points, max_points=200),
        "raw_point_count": len(points),
        "autopilot_share": path_autopilot_share(points),
    }


def _latest_alert_attrs(data: dict[str, Any]) -> dict[str, Any]:
    alert = latest_record(data.get("firmware_alerts", [])) or {}
    return {
        "description": alert.get("description"),
        "recent_fleet_count": alert.get("recent_fleet_count"),
        "timestamp": alert.get("timestamp"),
    }


def _latest_invoice_attrs(data: dict[str, Any]) -> dict[str, Any]:
    invoice = _latest_invoice(data) or {}
    return {
        "location": invoice.get("location"),
        "energy_used": invoice.get("energy_used"),
        "charging_fees": invoice.get("charging_fees"),
        "idle_fees": invoice.get("idle_fees"),
        "idle_minutes": invoice.get("idle_minutes"),
        "cost_per_kwh": invoice.get("cost_per_kwh"),
        "currency": invoice.get("currency"),
        "invoice_number": invoice.get("invoice_number"),
        "invoice_url": invoice.get("invoice_url"),
    }


def _display_name(key: str) -> str:
    """Create a readable English entity name from a stable key."""
    text = key.replace("_", " ")
    replacements = (
        ("autopilot fsd", "AP/FSD"),
        ("ap fsd", "AP/FSD"),
        ("supercharger", "Supercharger"),
        ("sentry", "Sentry"),
        ("kwh", "kWh"),
        ("vin", "VIN"),
    )
    for source, target in replacements:
        text = text.replace(source, target)
    return text[:1].upper() + text[1:] if text else key


def _s(
    key: str,
    name_key: str,
    value_fn: ValueFn,
    *,
    icon: str,
    device_class: SensorDeviceClass | None = None,
    unit: str | None = None,
    state_class: SensorStateClass | None = None,
    precision: int | None = None,
    enabled: bool = True,
    entity_category: EntityCategory | None = None,
    dynamic_currency: bool = False,
    invoice_currency: bool = False,
    currency_suffix: str | None = None,
    attributes_fn: AttributesFn | None = None,
    options: tuple[str, ...] | None = None,
) -> TessieSensorEntityDescription:
    return TessieSensorEntityDescription(
        key=key,
        name=_display_name(name_key),
        icon=icon,
        device_class=device_class,
        native_unit_of_measurement=unit,
        state_class=state_class,
        suggested_display_precision=precision,
        entity_registry_enabled_default=enabled,
        entity_category=entity_category,
        dynamic_currency=dynamic_currency,
        invoice_currency=invoice_currency,
        currency_suffix=currency_suffix,
        value_fn=value_fn,
        attributes_fn=attributes_fn,
        options=list(options) if options else None,
    )


__all__ = [name for name in globals() if not name.startswith("__")]
