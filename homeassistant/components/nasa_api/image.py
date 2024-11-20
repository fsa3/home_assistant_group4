"""Image entity for NASA APOD integration."""

from collections import deque
from datetime import UTC, datetime
import logging
from random import SystemRandom
from typing import cast

from httpx import AsyncClient, HTTPStatusError, RequestError

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DATA_SOURCES, DATA_SOURCE_APOD, DOMAIN
from .coordinator import NasaDataUpdateCoordinator
from .models import ApodImage

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the APOD image entity."""
    coordinator: NasaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    if DATA_SOURCE_APOD not in entry.data.get(CONF_DATA_SOURCES, []):
        _LOGGER.debug("APOD data source not enabled, skipping image entity setup")
        return

    async_add_entities([NasaApodImageEntity(coordinator, hass)])


class NasaApodImageEntity(CoordinatorEntity[NasaDataUpdateCoordinator], ImageEntity):
    """Representation of the APOD image entity."""

    _attr_name = "Astronomy Picture of the Day"
    _attr_unique_id = f"{DOMAIN}_apod_image"
    _attr_content_type = "image/jpeg"

    def __init__(
        self, coordinator: NasaDataUpdateCoordinator, hass: HomeAssistant
    ) -> None:
        """Initialize the APOD image entity."""
        super().__init__(coordinator)
        self._client: AsyncClient = get_async_client(hass)
        self.access_tokens: deque[str] = deque(maxlen=2)
        self.access_tokens.append(hex(SystemRandom().getrandbits(256))[2:])
        self._image_data: bytes | None = None
        self._attr_image_last_updated = datetime.now(UTC)

    @property
    def image_url(self) -> str | None:
        """Return the URL of the image."""
        apod_data = cast(ApodImage, self.coordinator.data.get(DATA_SOURCE_APOD))
        if apod_data and apod_data.media_type == "image":
            return apod_data.hdurl
        return None

    @property
    def available(self) -> bool:
        """Return if the entity is available."""
        apod_data = cast(ApodImage, self.coordinator.data.get(DATA_SOURCE_APOD))
        # only available if media type is image for now
        return apod_data is not None and apod_data.media_type == "image"

    async def async_image(self) -> bytes | None:
        """Return bytes of the image from the URL."""
        if self._image_data:
            _LOGGER.debug("Returning cached image data")
            return self._image_data

        image_url = self.image_url
        if not image_url:
            _LOGGER.error("APOD image URL is not available")
            return None

        try:
            response = await self._client.get(image_url)
            response.raise_for_status()
            self._image_data = response.content
        except HTTPStatusError as e:
            _LOGGER.error("HTTP error while fetching APOD image: %s", e)
            return None
        except RequestError as e:
            _LOGGER.error("Request error while fetching APOD image: %s", e)
            return None
        else:
            _LOGGER.debug("Fetched new image data from URL: %s", image_url)
            return self._image_data

    @property
    def image_last_updated(self) -> datetime | None:
        """Return the timestamp when the image was last updated."""
        return self._attr_image_last_updated

    async def async_update(self) -> None:
        """Update the image and refresh the last updated timestamp."""
        await super().async_update()
        # Reset the image data and update timestamp to force refresh
        self._image_data = None
        self._attr_image_last_updated = datetime.now(UTC)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return title and description of the image."""
        apod_data = cast(ApodImage, self.coordinator.data.get(DATA_SOURCE_APOD))
        if not apod_data:
            return {}
        return {
            "title": apod_data.title,
            "description": apod_data.explanation,
        }
