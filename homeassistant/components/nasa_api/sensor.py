"""Sensor platform for NASA NEO integration."""

from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, UnitOfLength, UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DATA_SOURCES, DATA_SOURCE_NEOWS, DOMAIN
from .coordinator import NasaDataUpdateCoordinator
from .models import NeoWsAsteroid

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by NASA API"

# Define descriptions for the NEO summary sensors
SUMMARY_SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="total_neo_count",
        name="Total NEO Count",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="hazardous_count",
        name="Potentially Hazardous NEOs",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="largest_diameter_meter",
        name="Largest NEO Diameter",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="smallest_diameter_meter",
        name="Smallest NEO Diameter",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="average_diameter_meter",
        name="Average NEO Diameter",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="closest_approach_km",
        name="Closest Approach Distance",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="farthest_approach_km",
        name="Farthest Approach Distance",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="fastest_velocity_kph",
        name="Fastest Velocity",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="slowest_velocity_kph",
        name="Slowest Velocity",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        entity_registry_enabled_default=True,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the summary sensor."""
    coordinator: NasaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if DATA_SOURCE_NEOWS not in entry.data.get(CONF_DATA_SOURCES, []):
        _LOGGER.debug("NEOWS data source not enabled, skipping summary sensor setup")
        return

    # Create sensors for each summary statistic
    summary_sensors = [
        NasaNeoSummarySensor(coordinator, desc) for desc in SUMMARY_SENSOR_DESCRIPTIONS
    ]
    async_add_entities(summary_sensors)


class NasaNeoSummarySensor(CoordinatorEntity[NasaDataUpdateCoordinator], SensorEntity):
    """Sensor entity for each NEO summary statistic."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NasaDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize each summary statistic sensor with its own description."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "nasa_neos")},
            name="Near Earth Objects",
            manufacturer="NASA",
            model="NeoWs API",
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_extra_state_attributes = {ATTR_ATTRIBUTION: ATTRIBUTION}

    @property
    def native_value(self) -> StateType:
        """Return the value for each specific statistic."""
        neows_data: list[NeoWsAsteroid] = cast(
            list[NeoWsAsteroid], self.coordinator.data.get(DATA_SOURCE_NEOWS, [])
        )
        if not neows_data:
            return None

        if self.entity_description.key == "total_neo_count":
            return len(neows_data)
        if self.entity_description.key == "hazardous_count":
            return sum(
                1 for asteroid in neows_data if asteroid.is_potentially_hazardous
            )
        if self.entity_description.key == "largest_diameter_meter":
            return round(
                max(
                    (asteroid.estimated_diameter.max_meters for asteroid in neows_data),
                    default=0,
                ),
                2,
            )
        if self.entity_description.key == "smallest_diameter_meter":
            return round(
                min(
                    (asteroid.estimated_diameter.min_meters for asteroid in neows_data),
                    default=0,
                ),
                2,
            )
        if self.entity_description.key == "average_diameter_meter":
            return round(
                sum(
                    asteroid.estimated_diameter.max_meters
                    + asteroid.estimated_diameter.min_meters
                    for asteroid in neows_data
                )
                / (2 * len(neows_data)),
                2,
            )
        if self.entity_description.key == "closest_approach_km":
            return round(
                min(
                    (
                        approach.miss_distance_km
                        for asteroid in neows_data
                        for approach in asteroid.close_approach_data
                    ),
                    default=0,
                ),
                2,
            )
        if self.entity_description.key == "farthest_approach_km":
            return round(
                max(
                    (
                        approach.miss_distance_km
                        for asteroid in neows_data
                        for approach in asteroid.close_approach_data
                    ),
                    default=0,
                ),
                2,
            )
        if self.entity_description.key == "fastest_velocity_kph":
            return round(
                max(
                    (
                        approach.relative_velocity_kph
                        for asteroid in neows_data
                        for approach in asteroid.close_approach_data
                    ),
                    default=0,
                ),
                2,
            )
        if self.entity_description.key == "slowest_velocity_kph":
            return round(
                min(
                    (
                        approach.relative_velocity_kph
                        for asteroid in neows_data
                        for approach in asteroid.close_approach_data
                    ),
                    default=0,
                ),
                2,
            )
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed information for all asteroids as attributes."""
        neows_data: list[NeoWsAsteroid] = cast(
            list[NeoWsAsteroid], self.coordinator.data.get(DATA_SOURCE_NEOWS, [])
        )
        if not neows_data:
            return {}

        asteroids = [
            {
                "id": asteroid.id,
                "name": asteroid.name,
                "url": asteroid.nasa_jpl_url,
                "max_diameter_m": round(asteroid.estimated_diameter.max_meters, 2),
                "min_diameter_m": round(asteroid.estimated_diameter.min_meters, 2),
                "hazardous": "Yes" if asteroid.is_potentially_hazardous else "No",
                "close_approach_date": asteroid.close_approach_data[
                    0
                ].close_approach_date_full
                if asteroid.close_approach_data
                else "",
                "miss_distance_km": round(
                    asteroid.close_approach_data[0].miss_distance_km, 2
                )
                if asteroid.close_approach_data
                else None,
                "relative_velocity_kph": round(
                    asteroid.close_approach_data[0].relative_velocity_kph, 2
                )
                if asteroid.close_approach_data
                else None,
            }
            for asteroid in neows_data
        ]

        # Sort asteroids by close_approach_date
        asteroids.sort(
            key=lambda x: datetime.strptime(x["close_approach_date"], "%Y-%b-%d %H:%M")
            if isinstance(x["close_approach_date"], str) and x["close_approach_date"]
            else datetime.max
        )

        # Filter out and show only relevant asteroids for applicable sensors

        if self.entity_description.key == "hazardous_count":
            hazardous_asteroids = [
                asteroid for asteroid in asteroids if asteroid["hazardous"] == "Yes"
            ]
            return {
                "asteroids": hazardous_asteroids,
            }

        attribute_key = self.entity_description.key

        if attribute_key == "closest_approach_km":
            return self._find_extreme_asteroid(
                asteroids, "miss_distance_km", "min", "closest_asteroid"
            )

        if attribute_key == "farthest_approach_km":
            return self._find_extreme_asteroid(
                asteroids, "miss_distance_km", "max", "farthest_asteroid"
            )

        if attribute_key == "largest_diameter_meter":
            return self._find_extreme_asteroid(
                asteroids, "max_diameter_m", "max", "largest_asteroid"
            )

        if attribute_key == "smallest_diameter_meter":
            return self._find_extreme_asteroid(
                asteroids, "min_diameter_m", "min", "smallest_asteroid"
            )

        if attribute_key == "fastest_velocity_kph":
            return self._find_extreme_asteroid(
                asteroids, "relative_velocity_kph", "max", "fastest_asteroid"
            )

        if attribute_key == "slowest_velocity_kph":
            return self._find_extreme_asteroid(
                asteroids, "relative_velocity_kph", "min", "slowest_asteroid"
            )

        return {
            "asteroids": asteroids,
        }

    def _find_extreme_asteroid(
        self,
        asteroids: list[dict[str, Any]],
        field: str,
        type: str,
        attribute_name: str,
    ) -> dict[str, Any]:
        """Find the extreme (min or max) asteroid based on a specific field."""
        if type not in ("max", "min"):
            raise ValueError("type must be either min or max")

        # Determine the default value for comparison
        default_value = float("inf") if type == "min" else float("-inf")

        # Handle empty asteroid list
        if not asteroids:
            return {}

        # Extract the extreme asteroid
        if type == "min":
            extreme_asteroid = min(
                asteroids,
                key=lambda x: float(x[field])
                if isinstance(x[field], (int, float, str))
                else default_value,
            )
        else:
            extreme_asteroid = max(
                asteroids,
                key=lambda x: float(x[field])
                if isinstance(x[field], (int, float, str))
                else default_value,
            )

        return {attribute_name: extreme_asteroid} if extreme_asteroid else {}
