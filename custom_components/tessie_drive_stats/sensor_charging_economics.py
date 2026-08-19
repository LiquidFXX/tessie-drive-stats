"""Charging Economics sensors for Tessie Drive Stats v0.6."""

from __future__ import annotations

from typing import Any

from .charging_economics import charging_economics
from .sensor_common import *  # noqa: F403

_CACHE_SOURCE: dict[str, Any] | None = None
_CACHE_RESULT: dict[str, Any] = {}


def _economics(data: dict[str, Any]) -> dict[str, Any]:
    """Calculate once per coordinator data object and reuse across entities."""
    global _CACHE_SOURCE, _CACHE_RESULT
    if data is not _CACHE_SOURCE:
        _CACHE_SOURCE = data
        _CACHE_RESULT = charging_economics(data)
    return _CACHE_RESULT


def _value(data: dict[str, Any], key: str) -> Any:
    return _economics(data).get(key)


SENSORS: list[TessieSensorEntityDescription] = [  # noqa: F405
    _s(
        "last_charge_efficiency",
        "last_charge_efficiency",
        lambda d: _value(d, "last_charge_efficiency"),
        icon="mdi:battery-charging-high",
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    _s(
        "last_charge_loss",
        "last_charge_loss",
        lambda d: _value(d, "last_charge_loss"),
        icon="mdi:transmission-tower-export",
        unit=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    _s(
        "last_charge_cost_per_kwh",
        "last_charge_cost_per_kwh",
        lambda d: _value(d, "last_charge_cost_per_kwh"),
        icon="mdi:cash-sync",
        state_class=SensorStateClass.MEASUREMENT,
        precision=4,
        currency_suffix="/kWh",
    ),
    _s(
        "last_supercharger_cost_per_kwh",
        "last_supercharger_cost_per_kwh",
        lambda d: _value(d, "last_supercharger_cost_per_kwh"),
        icon="mdi:ev-station",
        state_class=SensorStateClass.MEASUREMENT,
        precision=4,
        currency_suffix="/kWh",
    ),
]

for suffix in ("today", "this_week", "this_month", "this_year"):
    SENSORS.extend(
        [
            _s(
                f"charging_efficiency_{suffix}",
                f"charging_efficiency_{suffix}",
                lambda d, s=suffix: _value(d, f"charging_efficiency_{s}"),
                icon="mdi:battery-charging-high",
                unit=PERCENTAGE,
                state_class=SensorStateClass.MEASUREMENT,
                precision=1,
            ),
            _s(
                f"charging_loss_{suffix}",
                f"charging_loss_{suffix}",
                lambda d, s=suffix: _value(d, f"charging_loss_{s}"),
                icon="mdi:transmission-tower-export",
                unit=PERCENTAGE,
                state_class=SensorStateClass.MEASUREMENT,
                precision=1,
            ),
            _s(
                f"average_charging_cost_per_kwh_{suffix}",
                f"average_charging_cost_per_kwh_{suffix}",
                lambda d, s=suffix: _value(
                    d, f"average_charging_cost_per_kwh_{s}"
                ),
                icon="mdi:cash-sync",
                state_class=SensorStateClass.MEASUREMENT,
                precision=4,
                currency_suffix="/kWh",
            ),
            _s(
                f"charging_cost_coverage_{suffix}",
                f"charging_cost_coverage_{suffix}",
                lambda d, s=suffix: _value(d, f"charging_cost_coverage_{s}"),
                icon="mdi:chart-donut",
                unit=PERCENTAGE,
                state_class=SensorStateClass.MEASUREMENT,
                precision=1,
            ),
            _s(
                f"estimated_drive_cost_per_mile_{suffix}",
                f"estimated_drive_cost_per_mile_{suffix}",
                lambda d, s=suffix: _value(
                    d, f"estimated_drive_cost_per_mile_{s}"
                ),
                icon="mdi:road-variant",
                state_class=SensorStateClass.MEASUREMENT,
                precision=4,
                currency_suffix="/mi",
            ),
            _s(
                f"estimated_driving_cost_{suffix}",
                f"estimated_driving_cost_{suffix}",
                lambda d, s=suffix: _value(d, f"estimated_driving_cost_{s}"),
                icon="mdi:car-electric",
                device_class=SensorDeviceClass.MONETARY,
                state_class=SensorStateClass.MEASUREMENT,
                precision=2,
                dynamic_currency=True,
            ),
        ]
    )

SENSORS.extend(
    [
        _s(
            "recorded_lifetime_charging_efficiency",
            "recorded_lifetime_charging_efficiency",
            lambda d: _value(d, "recorded_lifetime_charging_efficiency"),
            icon="mdi:battery-charging-high",
            unit=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            precision=1,
        ),
        _s(
            "recorded_lifetime_charging_loss",
            "recorded_lifetime_charging_loss",
            lambda d: _value(d, "recorded_lifetime_charging_loss"),
            icon="mdi:transmission-tower-export",
            unit=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            precision=1,
        ),
        _s(
            "recorded_lifetime_average_charging_cost_per_kwh",
            "recorded_lifetime_average_charging_cost_per_kwh",
            lambda d: _value(
                d, "recorded_lifetime_average_charging_cost_per_kwh"
            ),
            icon="mdi:cash-sync",
            state_class=SensorStateClass.MEASUREMENT,
            precision=4,
            currency_suffix="/kWh",
        ),
        _s(
            "recorded_lifetime_charging_cost_coverage",
            "recorded_lifetime_charging_cost_coverage",
            lambda d: _value(d, "recorded_lifetime_charging_cost_coverage"),
            icon="mdi:chart-donut",
            unit=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            precision=1,
        ),
        _s(
            "recorded_lifetime_economics_since",
            "recorded_lifetime_economics_since",
            lambda d: _timestamp(_value(d, "recorded_lifetime_economics_since")),
            icon="mdi:calendar-start",
            device_class=SensorDeviceClass.TIMESTAMP,
        ),
        _s(
            "recorded_lifetime_estimated_driving_cost",
            "recorded_lifetime_estimated_driving_cost",
            lambda d: _value(d, "recorded_lifetime_estimated_driving_cost"),
            icon="mdi:car-electric",
            device_class=SensorDeviceClass.MONETARY,
            state_class=SensorStateClass.MEASUREMENT,
            precision=2,
            dynamic_currency=True,
        ),
        _s(
            "recorded_lifetime_estimated_drive_cost_per_mile",
            "recorded_lifetime_estimated_drive_cost_per_mile",
            lambda d: _value(
                d, "recorded_lifetime_estimated_drive_cost_per_mile"
            ),
            icon="mdi:road-variant",
            state_class=SensorStateClass.MEASUREMENT,
            precision=4,
            currency_suffix="/mi",
        ),
        _s(
            "recorded_lifetime_non_supercharger_average_cost_per_kwh",
            "recorded_lifetime_non_supercharger_average_cost_per_kwh",
            lambda d: _value(
                d, "recorded_lifetime_non_supercharger_average_cost_per_kwh"
            ),
            icon="mdi:home-lightning-bolt-outline",
            state_class=SensorStateClass.MEASUREMENT,
            precision=4,
            currency_suffix="/kWh",
        ),
        _s(
            "recorded_lifetime_supercharger_average_cost_per_kwh",
            "recorded_lifetime_supercharger_average_cost_per_kwh",
            lambda d: _value(
                d, "recorded_lifetime_supercharger_average_cost_per_kwh"
            ),
            icon="mdi:ev-station",
            state_class=SensorStateClass.MEASUREMENT,
            precision=4,
            currency_suffix="/kWh",
        ),
        _s(
            "recorded_lifetime_supercharger_cost_premium",
            "recorded_lifetime_supercharger_cost_premium",
            lambda d: _value(d, "recorded_lifetime_supercharger_cost_premium"),
            icon="mdi:compare-horizontal",
            unit=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            precision=1,
        ),
    ]
)
