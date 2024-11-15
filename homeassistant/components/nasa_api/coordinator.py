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
            update_interval=timedelta(minutes=10),  # 10 sec
        )
        self.api_client = client
        self.cache: dict[str, NeoWsAsteroid] = {}

    async def _async_update_neows_data(self) -> list[NeoWsAsteroid]:
        """Fetch data from Neo API."""
        try:
            return await self.api_client.fetch_neos_data()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def _async_update_data(self) -> list[NeoWsAsteroid]:
        """Override method in HomeAssistants DataUpdateCoordinator to make data available to sensors."""
        return await self._async_update_neows_data()
