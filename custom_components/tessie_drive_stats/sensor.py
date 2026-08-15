"""Sensor platform for Tessie Drive Stats."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .calculations import (
    cost_since,
    drive_battery_used,
    drive_count,
    drive_efficiency,
    drive_energy,
    drive_miles,
    drive_time_minutes,
    record_battery_used,
    record_distance,
    record_efficiency,
    record_energy,
    record_location,
    record_time_minutes,
)
from .const import CONF_VIN, DOMAIN
from .coordinator import TessieDriveStatsCoordinator


@dataclass(frozen=True, kw_only=True)
class TessieSensorEntityDescription(SensorEntityDescription):
    """Describe a Tessie Drive Stats sensor."""

    value_fn: Callable[[dict[str, Any]], Any]
    dynamic_currency: bool = False


SENSORS: tuple[TessieSensorEntityDescription, ...] = (
    TessieSensorEntityDescription(
        key="drives_today",
        translation_key="drives_today",
        icon="mdi:car-multiple",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: drive_count(data["drives_today"]),
    ),
    TessieSensorEntityDescription(
        key="miles_today",
        translation_key="miles_today",
        icon="mdi:road-variant",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.MILES,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: drive_miles(data["drives_today"]),
    ),
    TessieSensorEntityDescription(
        key="energy_today",
        translation_key="energy_today",
        icon="mdi:lightning-bolt",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        value_fn=lambda data: drive_energy(data["drives_today"]),
    ),
    TessieSensorEntityDescription(
        key="drive_time_today",
        translation_key="drive_time_today",
        icon="mdi:clock-outline",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: drive_time_minutes(data["drives_today"]),
    ),
    TessieSensorEntityDescription(
        key="efficiency_today",
        translation_key="efficiency_today",
        icon="mdi:gauge",
        native_unit_of_measurement="Wh/mi",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: drive_efficiency(data["drives_today"]),
    ),
    TessieSensorEntityDescription(
        key="battery_used_today",
        translation_key="battery_used_today",
        icon="mdi:battery-minus",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: drive_battery_used(data["drives_today"]),
    ),
    TessieSensorEntityDescription(
        key="last_drive_miles",
        translation_key="last_drive_miles",
        icon="mdi:car",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.MILES,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: record_distance(data["last_drive"]),
    ),
    TessieSensorEntityDescription(
        key="last_drive_energy",
        translation_key="last_drive_energy",
        icon="mdi:lightning-bolt",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        value_fn=lambda data: record_energy(data["last_drive"]),
    ),
    TessieSensorEntityDescription(
        key="last_drive_time",
        translation_key="last_drive_time",
        icon="mdi:timer-outline",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: record_time_minutes(data["last_drive"]),
    ),
    TessieSensorEntityDescription(
        key="last_drive_efficiency",
        translation_key="last_drive_efficiency",
        icon="mdi:gauge",
        native_unit_of_measurement="Wh/mi",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: record_efficiency(data["last_drive"]),
    ),
    TessieSensorEntityDescription(
        key="last_drive_start",
        translation_key="last_drive_start",
        icon="mdi:map-marker",
        value_fn=lambda data: record_location(data["last_drive"], ending=False),
    ),
    TessieSensorEntityDescription(
        key="last_drive_destination",
        translation_key="last_drive_destination",
        icon="mdi:map-marker-check",
        value_fn=lambda data: record_location(data["last_drive"], ending=True),
    ),
    TessieSensorEntityDescription(
        key="last_drive_starting_battery",
        translation_key="last_drive_starting_battery",
        icon="mdi:battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: (
            None
            if data["last_drive"] is None
            else data["last_drive"].get("starting_battery")
        ),
    ),
    TessieSensorEntityDescription(
        key="last_drive_ending_battery",
        translation_key="last_drive_ending_battery",
        icon="mdi:battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: (
            None
            if data["last_drive"] is None
            else data["last_drive"].get("ending_battery")
        ),
    ),
    TessieSensorEntityDescription(
        key="last_drive_battery_used",
        translation_key="last_drive_battery_used",
        icon="mdi:battery-minus",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: record_battery_used(data["last_drive"]),
    ),
    TessieSensorEntityDescription(
        key="last_drive_average_speed",
        translation_key="last_drive_average_speed",
        icon="mdi:speedometer",
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: (
            None
            if data["last_drive"] is None
            else data["last_drive"].get("average_speed")
        ),
    ),
    TessieSensorEntityDescription(
        key="last_drive_max_speed",
        translation_key="last_drive_max_speed",
        icon="mdi:speedometer",
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: (
            None
            if data["last_drive"] is None
            else data["last_drive"].get("max_speed")
        ),
    ),
    TessieSensorEntityDescription(
        key="cost_today",
        translation_key="cost_today",
        icon="mdi:currency-usd",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        dynamic_currency=True,
        value_fn=lambda data: cost_since(
            data["charges_ytd"], data["boundaries"]["today"]
        ),
    ),
    TessieSensorEntityDescription(
        key="cost_this_week",
        translation_key="cost_this_week",
        icon="mdi:calendar-week",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        dynamic_currency=True,
        value_fn=lambda data: cost_since(
            data["charges_ytd"], data["boundaries"]["week"]
        ),
    ),
    TessieSensorEntityDescription(
        key="cost_this_month",
        translation_key="cost_this_month",
        icon="mdi:calendar-month",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        dynamic_currency=True,
        value_fn=lambda data: cost_since(
            data["charges_ytd"], data["boundaries"]["month"]
        ),
    ),
    TessieSensorEntityDescription(
        key="cost_this_year",
        translation_key="cost_this_year",
        icon="mdi:calendar",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        dynamic_currency=True,
        value_fn=lambda data: cost_since(
            data["charges_ytd"], data["boundaries"]["year"]
        ),
    ),
    TessieSensorEntityDescription(
        key="last_charge_cost",
        translation_key="last_charge_cost",
        icon="mdi:currency-usd",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        dynamic_currency=True,
        value_fn=lambda data: (
            None
            if data["last_charge"] is None
            else float(data["last_charge"].get("cost") or 0)
        ),
    ),
    TessieSensorEntityDescription(
        key="last_charge_energy_added",
        translation_key="last_charge_energy_added",
        icon="mdi:battery-charging",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        value_fn=lambda data: (
            None
            if data["last_charge"] is None
            else float(data["last_charge"].get("energy_added") or 0)
        ),
    ),
    TessieSensorEntityDescription(
        key="last_charge_location",
        translation_key="last_charge_location",
        icon="mdi:ev-station",
        value_fn=lambda data: (
            None
            if data["last_charge"] is None
            else (
                data["last_charge"].get("saved_location")
                or data["last_charge"].get("location")
            )
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tessie Drive Stats sensors."""
    coordinator: TessieDriveStatsCoordinator = entry.runtime_data
    async_add_entities(
        TessieDriveStatsSensor(
            coordinator, entry, description, hass.config.currency
        )
        for description in SENSORS
    )


class TessieDriveStatsSensor(CoordinatorEntity[TessieDriveStatsCoordinator], SensorEntity):
    """Representation of a Tessie Drive Stats sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TessieDriveStatsCoordinator,
        entry: ConfigEntry,
        description: TessieSensorEntityDescription,
        currency: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description

        vin = entry.data[CONF_VIN]
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            manufacturer="Tesla",
            model="Vehicle history via Tessie",
            name=entry.title,
        )

        if description.dynamic_currency:
            self._attr_native_unit_of_measurement = currency

    @property
    def native_value(self) -> Any:
        """Return the sensor value from coordinator memory."""
        return self.entity_description.value_fn(self.coordinator.data)
