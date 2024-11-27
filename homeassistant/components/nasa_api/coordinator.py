"""Coordinator for NASA API."""

from datetime import timedelta
import logging
from typing import cast

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DATA_SOURCE_APOD, DATA_SOURCE_NEOWS, DOMAIN
from .models import ApodImage, NeoWsAsteroid
from .nasa_api_client import NasaApiClient

_LOGGER = logging.getLogger(__name__)


class NasaDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, list[NeoWsAsteroid] | ApodImage]]
):
    """Class to manage the NEO data fetching from the API."""

    def __init__(
        self, hass: HomeAssistant, client: NasaApiClient, sources: list[str]
    ) -> None:
        """Initialize the NASA data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN + "_coordinator",
            update_interval=timedelta(minutes=10),  # 10 min
        )
        self.api_client = client
        self.sources = sources
        self.cache: dict[str, list[NeoWsAsteroid] | ApodImage] = {}

    async def _async_update_neows_data(self) -> list[NeoWsAsteroid]:
        """Fetch data from Neo API."""
        try:
            neows_data = await self.api_client.fetch_neos_data()
            if neows_data:
                self.cache[DATA_SOURCE_NEOWS] = neows_data
                return neows_data
        except Exception as err:
            _LOGGER.warning(
                "Failed to fetch NEOWS data, using cached data. Error: %s", err
            )
            if DATA_SOURCE_NEOWS in self.cache:
                return cast(list[NeoWsAsteroid], self.cache[DATA_SOURCE_NEOWS])
            raise UpdateFailed(
                f"No cached data available and failed to fetch new data. Error: {err}"
            ) from err
        _LOGGER.warning(
            "Returning empty data as fallback due to missing fetch and cache"
        )
        return []

    async def _async_update_apod_data(self) -> ApodImage:
        """Fetch data from the APOD API."""
        apod_data = ApodImage(
            url="",
            title="",
            explanation="No data available",
            date="",
            hdurl="",
            media_type="",
        )

        try:
            apod_data = await self.api_client.fetch_apod_data()
        except Exception as err:
            _LOGGER.warning(
                "Failed to fetch APOD data, using cached data. Error: %s", err
            )
            if DATA_SOURCE_APOD in self.cache:
                return cast(ApodImage, self.cache[DATA_SOURCE_APOD])
            raise UpdateFailed(
                f"No cached APOD data available and failed to fetch new data. Error: {err}"
            ) from err

        if not apod_data or apod_data.media_type != "image":
            _LOGGER.warning(
                "APOD data is invalid or media type is not 'image', using cached data"
            )
            if DATA_SOURCE_APOD in self.cache:
                return cast(ApodImage, self.cache[DATA_SOURCE_APOD])
            raise UpdateFailed(
                "Fetched APOD data is invalid and no cached data is available."
            )

        if apod_data:
            self.cache[DATA_SOURCE_APOD] = apod_data
            return apod_data

        return apod_data

    async def _async_update_data(self) -> dict[str, list[NeoWsAsteroid] | ApodImage]:
        """Override method in HomeAssistants DataUpdateCoordinator to make data available to sensors."""
        data: dict[str, list[NeoWsAsteroid] | ApodImage] = {}

        if DATA_SOURCE_NEOWS in self.sources:
            data[DATA_SOURCE_NEOWS] = await self._async_update_neows_data()

        if DATA_SOURCE_APOD in self.sources:
            data[DATA_SOURCE_APOD] = await self._async_update_apod_data()

        return data
