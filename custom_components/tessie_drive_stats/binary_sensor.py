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
from .device_groups import (
    GROUP_MODELS,
    GROUP_VEHICLE,
    binary_sensor_device_group,
    device_identifier,
    device_name,
)
from .efficiency import efficiency_intelligence


@dataclass(frozen=True, kw_only=True)
class TessieBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a Tessie Drive Stats binary sensor."""

    value_fn: Callable[[dict[str, Any]], bool | None]


def _tire_low(data: dict[str, Any], position: str) -> bool | None:
    status = (data.get("tire_pressure") or {}).get(f"{position}_status")
    if status is None or str(status).lower() == "unknown":
        return None
    return str(status).lower() == "low"


def _unusually_inefficient(data: dict[str, Any]) -> bool | None:
    """Flag a last drive at least 20% above a recent baseline with enough samples."""
    result = efficiency_intelligence(data)
    if result.get("vs_30_day_percent") is None or result.get("recent_30_day_drives", 0) < 5:
        return None
    return bool(result.get("unusually_inefficient"))


BINARY_SENSORS: tuple[TessieBinarySensorEntityDescription, ...] = tuple(
    [
        TessieBinarySensorEntityDescription(
            key=f"tire_pressure_low_{position}",
            name=f"{position.replace('_', ' ').title()} tire pressure low",
            icon="mdi:car-tire-alert",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value_fn=lambda data, p=position: _tire_low(data, p),
        )
        for position in ("front_left", "front_right", "rear_left", "rear_right")
    ]
    + [
        TessieBinarySensorEntityDescription(
            key="last_drive_unusually_inefficient",
            name="Last drive unusually inefficient",
            icon="mdi:gauge-alert",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value_fn=_unusually_inefficient,
        )
    ]
)


def _device_info(entry: ConfigEntry, group: str) -> DeviceInfo:
    """Build device metadata for a binary sensor's analytics group."""
    vin = entry.data[CONF_VIN]
    info = DeviceInfo(
        identifiers={(DOMAIN, device_identifier(vin, group))},
        manufacturer="Tesla" if group == GROUP_VEHICLE else "Tessie Drive Stats",
        model=GROUP_MODELS[group],
        name=device_name(entry.title, group),
    )
    if group != GROUP_VEHICLE:
        info["via_device"] = (DOMAIN, vin)
    return info


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
        self._attr_device_info = _device_info(
            entry,
            binary_sensor_device_group(description.key),
        )

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data)
