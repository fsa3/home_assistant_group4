"""Sensor platform for NASA API integration."""
# Generated placeholder sensor file
# Change everything in this file

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up NASA API sensor entities from a config entry."""
    LOGGER.info("Setting up NASA API sensor entities")

    # Retrieve the API client from the hass.data dictionary
    api_client = hass.data[DOMAIN][entry.entry_id]

    # Create a basic sensor entity (this is a placeholder, implement actual sensors later)
    sensor = NasaApiSensor(api_client)
    async_add_entities([sensor], update_before_add=True)


class NasaApiSensor(SensorEntity):
    """A basic sensor for the NASA API integration."""

    _attr_name = "NASA API Sensor"
    _attr_native_value: str | None = None

    def __init__(self, api_client) -> None:
        """Initialize the sensor."""
        self.api_client = api_client

    async def async_update(self) -> None:
        """Fetch new data from the NASA API."""
        # Placeholder update logic (replace with actual API calls later)
        self._attr_native_value = "No data"
