"""Sensor platform for NASA NEO integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NasaDataUpdateCoordinator
from .models import NeoWsAsteroid

_LOGGER = logging.getLogger(__name__)

# Define descriptions for the main NEO summary sensors
SUMMARY_SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(key="total_neo_count", name="Total NEO Count"),
    SensorEntityDescription(key="hazardous_count", name="Potentially Hazardous NEOs"),
    SensorEntityDescription(
        key="largest_diameter_km", name="Largest NEO Diameter (km)"
    ),
    SensorEntityDescription(
        key="smallest_diameter_km", name="Smallest NEO Diameter (km)"
    ),
    SensorEntityDescription(
        key="average_diameter_km", name="Average NEO Diameter (km)"
    ),
    SensorEntityDescription(
        key="closest_approach_km", name="Closest Approach Distance (km)"
    ),
    SensorEntityDescription(
        key="farthest_approach_km", name="Farthest Approach Distance (km)"
    ),
    SensorEntityDescription(key="fastest_velocity_kph", name="Fastest Velocity (km/h)"),
    SensorEntityDescription(key="slowest_velocity_kph", name="Slowest Velocity (km/h)"),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for each asteroid and the summary sensors."""
    coordinator: NasaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a sensor for each asteroid and individual sensors for each summary statistic
    asteroid_sensors: list[SensorEntity] = [
        NasaAsteroidSensor(coordinator, asteroid) for asteroid in coordinator.data
    ]
    summary_sensors: list[SensorEntity] = [
        NasaNeoSummarySensor(coordinator, desc) for desc in SUMMARY_SENSOR_DESCRIPTIONS
    ]
    all_sensors: list[SensorEntity] = asteroid_sensors + summary_sensors
    async_add_entities(all_sensors)


class NasaAsteroidSensor(CoordinatorEntity[NasaDataUpdateCoordinator], SensorEntity):
    """Representation of a single asteroid as a sensor entity."""

    def __init__(
        self, coordinator: NasaDataUpdateCoordinator, asteroid: NeoWsAsteroid
    ) -> None:
        """Initialize the asteroid sensor with specific asteroid details."""
        super().__init__(coordinator)
        self.asteroid = asteroid
        self._attr_name = f"Asteroid {asteroid.name}"
        self._attr_unique_id = f"{DOMAIN}_{asteroid.id}"

    @property
    def native_value(self) -> StateType:
        """Return the asteroid's absolute magnitude as the primary value."""
        return self.asteroid.absolute_magnitude_h

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional details about the asteroid."""
        return {
            "id": self.asteroid.id,
            "name": self.asteroid.name,
            "magnitude": self.asteroid.absolute_magnitude_h,
            "diameter_km": self.asteroid.estimated_diameter.max_km,
            "hazardous": "Yes" if self.asteroid.is_potentially_hazardous else "No",
            "close_approach_date": self.asteroid.close_approach_data[
                0
            ].close_approach_date
            if self.asteroid.close_approach_data
            else None,
            "miss_distance_km": self.asteroid.close_approach_data[0].miss_distance_km
            if self.asteroid.close_approach_data
            else None,
            "relative_velocity_kph": self.asteroid.close_approach_data[
                0
            ].relative_velocity_kph
            if self.asteroid.close_approach_data
            else None,
        }


class NasaNeoSummarySensor(CoordinatorEntity[NasaDataUpdateCoordinator], SensorEntity):
    """Sensor entity for each NEO summary statistic."""

    def __init__(
        self,
        coordinator: NasaDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize each summary statistic sensor with its own description."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the value for each specific statistic."""
        # Calculate statistics only when data is available
        if not self.coordinator.data:
            return None

        if self.entity_description.key == "total_neo_count":
            return len(self.coordinator.data)
        if self.entity_description.key == "hazardous_count":
            return sum(
                1
                for asteroid in self.coordinator.data
                if asteroid.is_potentially_hazardous
            )
        if self.entity_description.key == "largest_diameter_km":
            return max(
                (
                    asteroid.estimated_diameter.max_km
                    for asteroid in self.coordinator.data
                ),
                default=0,
            )
        if self.entity_description.key == "smallest_diameter_km":
            return min(
                (
                    asteroid.estimated_diameter.min_km
                    for asteroid in self.coordinator.data
                ),
                default=0,
            )
        if self.entity_description.key == "average_diameter_km":
            return sum(
                asteroid.estimated_diameter.max_km + asteroid.estimated_diameter.min_km
                for asteroid in self.coordinator.data
            ) / (2 * len(self.coordinator.data))
        if self.entity_description.key == "closest_approach_km":
            return min(
                (
                    approach.miss_distance_km
                    for asteroid in self.coordinator.data
                    for approach in asteroid.close_approach_data
                ),
                default=0,
            )
        if self.entity_description.key == "farthest_approach_km":
            return max(
                (
                    approach.miss_distance_km
                    for asteroid in self.coordinator.data
                    for approach in asteroid.close_approach_data
                ),
                default=0,
            )
        if self.entity_description.key == "fastest_velocity_kph":
            return max(
                (
                    approach.relative_velocity_kph
                    for asteroid in self.coordinator.data
                    for approach in asteroid.close_approach_data
                ),
                default=0,
            )
        if self.entity_description.key == "slowest_velocity_kph":
            return min(
                (
                    approach.relative_velocity_kph
                    for asteroid in self.coordinator.data
                    for approach in asteroid.close_approach_data
                ),
                default=0,
            )
        return None
