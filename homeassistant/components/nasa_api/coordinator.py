"""Coordinator for NASA API."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .models import NeoWsAsteroid
from .nasa_api_client import NasaApiClient

_LOGGER = logging.getLogger(__name__)


class NasaDataUpdateCoordinator(DataUpdateCoordinator[list[NeoWsAsteroid]]):
    """Class to manage the NEO data fetching from the API."""

    def __init__(self, hass: HomeAssistant, client: NasaApiClient) -> None:
        """Initialize the NASA data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN + "_NEO_COORDINATOR",
            update_interval=timedelta(minutes=10),  # 10 min
        )
        self.api_client = client
        self.cache: dict[str, list[NeoWsAsteroid]] = {}

    async def _async_update_neows_data(self) -> list[NeoWsAsteroid]:
        """Fetch data from Neo API."""
        try:
            neows_data = await self.api_client.fetch_neos_data()
            if neows_data:
                self.cache["neows"] = neows_data
                return neows_data
        except Exception as err:
            _LOGGER.warning(
                "Failed to fetch NEOWS data, using cached data. Error: %s", err
            )
            if "neows" in self.cache:
                return self.cache["neows"]
            raise UpdateFailed(
                f"No cached data available and failed to fetch new data. Error: {err}"
            ) from err
        _LOGGER.warning(
            "Returning empty data as fallback due to missing fetch and cache"
        )
        return []

    async def _async_update_data(self) -> list[NeoWsAsteroid]:
        """Override method in HomeAssistants DataUpdateCoordinator to make data available to sensors."""
        return await self._async_update_neows_data()
