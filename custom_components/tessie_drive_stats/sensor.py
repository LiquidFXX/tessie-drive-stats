"""Sensor platform for Tessie Drive Stats."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_VIN, DOMAIN
from .coordinator import TessieDriveStatsCoordinator
from .sensor_battery import SENSORS as BATTERY_SENSORS
from .sensor_charge_idle import SENSORS as CHARGE_IDLE_SENSORS
from .sensor_common import TessieSensorEntityDescription, _invoice_currency
from .sensor_drive import SENSORS as DRIVE_SENSORS
from .sensor_efficiency import SENSORS as EFFICIENCY_SENSORS
from .sensor_lifetime import SENSORS as LIFETIME_SENSORS
from .sensor_vehicle import SENSORS as VEHICLE_SENSORS

SENSORS_TUPLE = tuple(
    DRIVE_SENSORS
    + EFFICIENCY_SENSORS
    + CHARGE_IDLE_SENSORS
    + BATTERY_SENSORS
    + LIFETIME_SENSORS
    + VEHICLE_SENSORS
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tessie Drive Stats sensors."""
    coordinator: TessieDriveStatsCoordinator = entry.runtime_data
    async_add_entities(
        TessieDriveStatsSensor(coordinator, entry, description, hass.config.currency)
        for description in SENSORS_TUPLE
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
        self._currency = currency

        vin = entry.data[CONF_VIN]
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            manufacturer="Tesla",
            model="Vehicle analytics via Tessie",
            name=entry.title,
        )

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def native_unit_of_measurement(self) -> str | None:
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
