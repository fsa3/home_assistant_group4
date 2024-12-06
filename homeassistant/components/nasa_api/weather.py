"""Weather platform for NASA API integration."""

from collections.abc import Mapping
from typing import Any, cast

from homeassistant.components.weather import WeatherEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_SOURCE_INSIGHT, DOMAIN, LOGGER
from .coordinator import NasaDataUpdateCoordinator
from .models import MarsWeather

CONDITION_MAPPING = {
    "winter": "snowy",
    "spring": "sunny",
    "summer": "clear",
    "fall": "partlycloudy",
}

SEASON_DESCRIPTIONS = {
    "winter": "Cold and dry",
    "spring": "Warming up",
    "summer": "Hot and windy",
    "fall": "Cooling down",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Weather platform for NASA API integration."""
    coordinator: NasaDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    if DATA_SOURCE_INSIGHT not in coordinator.sources:
        LOGGER.debug("DATA_SOURCE_INSIGHT is not in the selected sources")
        return

    async_add_entities([MarsWeatherEntity(coordinator)])


class MarsWeatherEntity(CoordinatorEntity[NasaDataUpdateCoordinator], WeatherEntity):
    """Representation of Mars Weather as a WeatherEntity."""

    _attr_name = "Mars Weather"
    _attr_unique_id = f"{DOMAIN}_mars_weather"

    def __init__(self, coordinator: NasaDataUpdateCoordinator) -> None:
        """Initialize the Mars Weather entity."""
        super().__init__(coordinator)
        LOGGER.debug("Initialized MarsWeatherEntity")

    def _latest_sol_data(self) -> MarsWeather | None:
        """Retrieve the latest sol data from the coordinator."""
        raw_data = self.coordinator.data.get(DATA_SOURCE_INSIGHT, [])
        if isinstance(raw_data, list) and raw_data:
            return cast(MarsWeather, raw_data[-1])  # Latest sol data
        LOGGER.warning("No latest sol data available")
        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        sol_data = self._latest_sol_data()
        if sol_data:
            value = sol_data.temperature
            LOGGER.debug(f"Temperature for Sol {sol_data.sol}: {value}")
            return value
        return None

    @property
    def native_pressure(self) -> float | None:
        """Return the current atmospheric pressure."""
        sol_data = self._latest_sol_data()
        if sol_data:
            value = sol_data.pressure
            LOGGER.debug(f"Pressure for Sol {sol_data.sol}: {value}")
            return value
        return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed."""
        sol_data = self._latest_sol_data()
        if sol_data:
            value = sol_data.wind_speed
            LOGGER.debug(f"Wind Speed for Sol {sol_data.sol}: {value}")
            return value
        return None

    @property
    def condition(self) -> str | None:
        """Return a human-readable representation of the weather condition."""
        sol_data = self._latest_sol_data()
        if sol_data and sol_data.season:
            season = sol_data.season.lower()
            return CONDITION_MAPPING.get(season, "unknown")
        return "unknown"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra attributes for debugging or additional info."""
        sol_data = self._latest_sol_data()
        if not sol_data:
            return None

        attrs = {
            "sol": sol_data.sol,
            "temperature_min": sol_data.temperature_min,
            "temperature_max": sol_data.temperature_max,
            "pressure": sol_data.pressure,
            "season": sol_data.season,
            "wind_speed": sol_data.wind_speed,
            "wind_bearing": sol_data.wind_bearing,
        }
        LOGGER.debug(f"Extra state attributes for Sol {sol_data.sol}: {attrs}")
        return attrs
