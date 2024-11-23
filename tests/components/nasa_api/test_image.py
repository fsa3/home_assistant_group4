"""Test file for Image.py in the NASA_API components."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.components.nasa_api.const import (
    CONF_DATA_SOURCES,
    DATA_SOURCE_APOD,
    DOMAIN,
)
from homeassistant.components.nasa_api.image import (
    NasaApodImageEntity,
    async_setup_entry,
)
from homeassistant.components.nasa_api.models import ApodImage
from homeassistant.core import HomeAssistant


@pytest.fixture
def mock_coordinator() -> MagicMock:
    """Create a mock coordinator with sample APOD data."""
    return MagicMock(
        data={
            DATA_SOURCE_APOD: ApodImage(
                date="2024-01-01",
                url="http://example.com/mock-image-standard.jpg",
                title="Mock Image Title",
                explanation="Mock description of the APOD image.",
                media_type="image",
                hdurl="http://example.com/mock-image-hd.jpg",
            )
        }
    )


# 1 test entity setup
@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant, mock_coordinator) -> None:
    """Test setting up the APOD image entity."""
    # Mock ConfigEntry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {CONF_DATA_SOURCES: [DATA_SOURCE_APOD]}  # Enable APOD source

    # Inject mock coordinator into hass.data
    hass.data = {DOMAIN: {entry.entry_id: mock_coordinator}}

    # Mock async_add_entities
    async_add_entities = AsyncMock()

    # Run the async_setup_entry function
    await async_setup_entry(hass, entry, async_add_entities)

    # Verify the entity was added
    async_add_entities.assert_called_once()
    added_entities = async_add_entities.call_args[0][0]
    assert len(added_entities) == 1
    assert isinstance(added_entities[0], NasaApodImageEntity)


# 2 Test image URL retrieval
def test_image_url(mock_coordinator) -> None:
    """Test the image_url property of the NasaApodImageEntity."""
    # Create the entity with the mock coordinator
    entity = NasaApodImageEntity(mock_coordinator, MagicMock())

    # Case 1: Valid image data
    assert (
        entity.image_url == "http://example.com/mock-image-hd.jpg"
    ), "Expected hdurl for valid image data"

    # Case 2: Invalid media type
    mock_coordinator.data[DATA_SOURCE_APOD].media_type = "video"
    assert entity.image_url is None, "Expected None for invalid media type"

    # Case 3: Missing data
    mock_coordinator.data[DATA_SOURCE_APOD] = None
    assert entity.image_url is None, "Expected None for missing data"


# 3 Test Entity Availability
def test_available(mock_coordinator) -> None:
    """Test the available property of the NasaApodImageEntity."""
    entity = NasaApodImageEntity(mock_coordinator, MagicMock())

    # Case 1: Valid data
    assert (
        entity.available is True
    ), "Expected available to be True for valid image data"

    # Case 2: Invalid media type
    mock_coordinator.data[DATA_SOURCE_APOD].media_type = "video"
    assert (
        entity.available is False
    ), "Expected available to be False for invalid media type"

    # Case 3: Missing data
    mock_coordinator.data[DATA_SOURCE_APOD] = None
    assert entity.available is False, "Expected available to be False for missing data"


# 4 Test Image Retrieval


# 5 Test extra state Attributes
