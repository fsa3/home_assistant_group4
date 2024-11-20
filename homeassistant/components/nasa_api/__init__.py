"""The NASA API integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_KEY, CONF_DATA_SOURCES, DEFAULT_API_KEY, DOMAIN, LOGGER
from .coordinator import NasaDataUpdateCoordinator
from .nasa_api_client import NasaApiClient

PLATFORMS: list[Platform] = [Platform.IMAGE, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NASA API from a config entry."""

    # Initialize domain in hass data
    hass.data.setdefault(DOMAIN, {})

    # Check if API client is already set up
    if entry.entry_id in hass.data[DOMAIN]:
        LOGGER.warning("NASA API integration already set up, setup aborted")
        return False

    session = async_get_clientsession(hass)
    api_client = NasaApiClient(
        api_key=entry.data.get(CONF_API_KEY, DEFAULT_API_KEY), session=session
    )

    # Get the selected data sources from the config entry
    selected_sources = entry.data.get(CONF_DATA_SOURCES, [])

    nasa_coordinator = NasaDataUpdateCoordinator(hass, api_client, selected_sources)
    await nasa_coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = nasa_coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    LOGGER.info("NASA API integration setup complete")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    LOGGER.info("NASA API integration unloaded")
    return unload_ok
