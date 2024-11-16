"""Sensor platform for NASA NEO integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NasaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Define the sensor description specifically for the asteroid count
SENSOR_DESCRIPTION = SensorEntityDescription(
    key="neo_count",
    name="NEO Count",
    state_class=SensorStateClass.MEASUREMENT,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the NEO count sensor."""
    coordinator: NasaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NasaNeoCountSensor(coordinator)])


class NasaNeoCountSensor(CoordinatorEntity[NasaDataUpdateCoordinator], SensorEntity):
    """Representation of the NEO count sensor."""

    _attr_has_entity_name = True
    _attr_entity_description = SENSOR_DESCRIPTION

    def __init__(self, coordinator: NasaDataUpdateCoordinator) -> None:
        """Initialize the NEO count sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_neo_count"
        self._attr_name = "Number of Near-Earth Objects"

    @property
    def native_value(self) -> StateType:
        """Return the current count of near-Earth objects for today."""
        # Get the count directly from the coordinator's data
        if not isinstance(self.coordinator.data, list):
            return 0
        return len(self.coordinator.data) if self.coordinator.data else 0
