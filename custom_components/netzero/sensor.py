"""Sensor platform for Netzero Energy."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DESCRIPTIONS
from .coordinator import NetzeroDataUpdateCoordinator

type NetzeroConfigEntry = ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NetzeroConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Netzero sensors."""
    coordinator: NetzeroDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities = [
        NetzeroSensor(
            coordinator=coordinator,
            entry_id=entry.entry_id,
            description=description,
        )
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class NetzeroSensor(CoordinatorEntity[NetzeroDataUpdateCoordinator], SensorEntity):
    """Representation of a Netzero sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NetzeroDataUpdateCoordinator,
        entry_id: str,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.site_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.site_id)},
            name=f"Netzero {coordinator.site_id}",
            manufacturer="Netzero",
            model="Solar",
            configuration_url="https://app.netzero.energy/",
        )

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        sensors = data.get("sensors", {})
        return sensors.get(self.entity_description.key)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "last_timestamp": data.get("last_timestamp"),
            "latency_ms": data.get("latency_ms"),
            "site_id": data.get("site_id"),
        }

