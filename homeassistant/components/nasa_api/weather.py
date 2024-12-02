"""Weather platform for NASA API integration."""

from collections.abc import Mapping
from typing import Any

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

    # Extract data for the latest sol
    raw_data = coordinator.data.get(DATA_SOURCE_INSIGHT, [])
    if not raw_data:
        LOGGER.warning("No data available for InSight Mars Weather")
        return

    # Assuming sol_keys are in sequential order
    latest_sol = raw_data[-1] if isinstance(raw_data, list) and raw_data else None

    if not isinstance(latest_sol, MarsWeather):
        LOGGER.error("Latest sol data is not of type MarsWeather")
        return

    # Create a single weather entity for the latest sol
    entity = MarsWeatherEntity(coordinator, latest_sol)

    async_add_entities([entity])


class MarsWeatherEntity(CoordinatorEntity, WeatherEntity):
    """Representation of Mars Weather as a WeatherEntity."""

    def __init__(
        self,
        coordinator: NasaDataUpdateCoordinator,
        sol_data: MarsWeather | list[MarsWeather],
    ) -> None:
        """Initialize the Mars Weather entity."""
        super().__init__(coordinator)

        # Ensure sol_data is iterable or handle it accordingly
        if isinstance(sol_data, list):
            self._sol_data = sol_data[0] if sol_data else None
        elif isinstance(sol_data, MarsWeather):
            self._sol_data = sol_data
        else:
            raise TypeError(
                f"Expected sol_data to be MarsWeather or list[MarsWeather], got {type(sol_data)}"
            )

        if self._sol_data is not None:
            self._attr_name = f"Mars Weather (Sol {self._sol_data.sol})"
            self._attr_unique_id = f"{DOMAIN}_mars_weather_{self._sol_data.sol}"
            LOGGER.debug(
                f"Initialized MarsWeatherEntity for Sol {self._sol_data.sol}: {self._sol_data}"
            )
        else:
            LOGGER.warning("No valid MarsWeather data provided")
            self._attr_name = "Mars Weather (Unknown Sol)"
            self._attr_unique_id = f"{DOMAIN}_mars_weather_unknown"

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        if self._sol_data:
            value = self._sol_data.temperature
            LOGGER.debug(f"Temperature for Sol {self._sol_data.sol}: {value}")
            return value
        return None

    @property
    def native_pressure(self) -> float | None:
        """Return the current atmospheric pressure."""
        if self._sol_data:
            value = self._sol_data.pressure
            LOGGER.debug(f"Pressure for Sol {self._sol_data.sol}: {value}")
            return value
        return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed."""
        if self._sol_data:
            value = self._sol_data.wind_speed
            LOGGER.debug(f"Wind Speed for Sol {self._sol_data.sol}: {value}")
            return value
        return None

    @property
    def condition(self) -> str | None:
        """Return a human-readable representation of the weather condition."""
        if self._sol_data and self._sol_data.season:
            season = self._sol_data.season.lower()

            # Map Mars seasons to Home Assistant weather conditions
            if season in ("early winter", "mid winter"):
                return "snowy"  # Maps to snowy condition
            if season in ("early summer", "mid summer"):
                return "sunny"
            if season == "fall":
                return "partlycloudy"
            return "unknown"
        return "unknown"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra attributes for debugging or additional info."""
        if not self._sol_data:
            return None

        attrs = {
            "sol": self._sol_data.sol,
            "temperature_min": self._sol_data.temperature_min,
            "temperature_max": self._sol_data.temperature_max,
            "pressure": self._sol_data.pressure,
            "season": self._sol_data.season,
            "wind_speed": self._sol_data.wind_speed,
            "wind_bearing": self._sol_data.wind_bearing,
        }
        LOGGER.debug(f"Extra state attributes for Sol {self._sol_data.sol}: {attrs}")
        return attrs
