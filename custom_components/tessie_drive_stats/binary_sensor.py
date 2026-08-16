"""Binary sensor platform for Tessie Drive Stats."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_VIN, DOMAIN
from .coordinator import TessieDriveStatsCoordinator


@dataclass(frozen=True, kw_only=True)
class TessieBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a Tessie Drive Stats binary sensor."""

    value_fn: Callable[[dict[str, Any]], bool | None]


def _tire_low(data: dict[str, Any], position: str) -> bool | None:
    status = (data.get("tire_pressure") or {}).get(f"{position}_status")
    if status is None or str(status).lower() == "unknown":
        return None
    return str(status).lower() == "low"


BINARY_SENSORS: tuple[TessieBinarySensorEntityDescription, ...] = tuple(
    TessieBinarySensorEntityDescription(
        key=f"tire_pressure_low_{position}",
        name=f"{position.replace('_', ' ').title()} tire pressure low",
        icon="mdi:car-tire-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data, p=position: _tire_low(data, p),
    )
    for position in ("front_left", "front_right", "rear_left", "rear_right")
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: TessieDriveStatsCoordinator = entry.runtime_data
    async_add_entities(
        TessieDriveStatsBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSORS
    )


class TessieDriveStatsBinarySensor(
    CoordinatorEntity[TessieDriveStatsCoordinator],
    BinarySensorEntity,
):
    """Representation of a Tessie Drive Stats binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TessieDriveStatsCoordinator,
        entry: ConfigEntry,
        description: TessieBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        vin = entry.data[CONF_VIN]
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            manufacturer="Tesla",
            model="Vehicle analytics via Tessie",
            name=entry.title,
        )

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data)
