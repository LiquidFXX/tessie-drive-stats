"""Sensor platform for Tessie Drive Stats."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import CONF_VIN, DOMAIN
from .coordinator import TessieDriveStatsCoordinator
from .device_groups import (
    GROUP_MODELS,
    GROUP_VEHICLE,
    device_identifier,
    device_name,
    sensor_device_group,
)
from .sensor_battery import SENSORS as BATTERY_SENSORS
from .sensor_charge_idle import SENSORS as CHARGE_IDLE_SENSORS
from .sensor_charging_economics import SENSORS as CHARGING_ECONOMICS_SENSORS
from .sensor_common import TessieSensorEntityDescription, _invoice_currency
from .sensor_drive import SENSORS as DRIVE_SENSORS
from .sensor_efficiency import SENSORS as EFFICIENCY_SENSORS
from .sensor_lifetime import SENSORS as LIFETIME_SENSORS
from .sensor_vehicle import SENSORS as VEHICLE_SENSORS

_SENSOR_SOURCES = (
    ("drive", DRIVE_SENSORS),
    ("efficiency", EFFICIENCY_SENSORS),
    ("charge_idle", CHARGE_IDLE_SENSORS),
    ("charging_economics", CHARGING_ECONOMICS_SENSORS),
    ("battery", BATTERY_SENSORS),
    ("lifetime", LIFETIME_SENSORS),
    ("vehicle", VEHICLE_SENSORS),
)

SENSORS_TUPLE = tuple(
    (description, sensor_device_group(source, description.key))
    for source, descriptions in _SENSOR_SOURCES
    for description in descriptions
)


def _ensure_parent_device(hass: HomeAssistant, entry: ConfigEntry) -> str:
    """Ensure the main vehicle device exists and return its registry ID."""
    vin = entry.data[CONF_VIN]
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, vin)},
        manufacturer="Tesla",
        model=GROUP_MODELS[GROUP_VEHICLE],
        name=entry.title,
    )
    return device.id


def _device_info(
    entry: ConfigEntry,
    group: str,
    parent_device_id: str,
) -> DeviceInfo:
    """Build device metadata for the physical vehicle or an analytics group."""
    vin = entry.data[CONF_VIN]
    if group == GROUP_VEHICLE:
        return DeviceInfo(
            identifiers={(DOMAIN, vin)},
            manufacturer="Tesla",
            model=GROUP_MODELS[group],
            name=entry.title,
        )

    return DeviceInfo(
        identifiers={(DOMAIN, device_identifier(vin, group))},
        manufacturer="Tessie Drive Stats",
        model=GROUP_MODELS[group],
        name=device_name(entry.title, group),
        via_device_id=parent_device_id,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tessie Drive Stats sensors."""
    coordinator: TessieDriveStatsCoordinator = entry.runtime_data
    parent_device_id = _ensure_parent_device(hass, entry)
    async_add_entities(
        TessieDriveStatsSensor(
            coordinator,
            entry,
            description,
            hass.config.currency,
            device_group,
            parent_device_id,
        )
        for description, device_group in SENSORS_TUPLE
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
        device_group: str,
        parent_device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._currency = currency
        self._vehicle_name = entry.title

        vin = entry.data[CONF_VIN]
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = _device_info(entry, device_group, parent_device_id)

    @property
    def suggested_object_id(self) -> str:
        """Keep generated entity IDs independent of analytics-device names."""
        return slugify(f"{self._vehicle_name}_{self.entity_description.key}")

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def native_unit_of_measurement(self) -> str | None:
        if self.entity_description.currency_suffix:
            return f"{self._currency}{self.entity_description.currency_suffix}"
        if self.entity_description.dynamic_currency:
            return self._currency
        if self.entity_description.invoice_currency:
            return _invoice_currency(self.coordinator.data) or self._currency
        return self.entity_description.native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attributes_fn is None:
            return None
        return self.entity_description.attributes_fn(self.coordinator.data)
