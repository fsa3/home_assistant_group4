"""Test for init file."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.components.nasa_api import async_unload_entry
from homeassistant.components.nasa_api.const import DOMAIN
from homeassistant.components.nasa_api.coordinator import NasaDataUpdateCoordinator
from homeassistant.components.nasa_api.nasa_api_client import NasaApiClient
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


@pytest.fixture
def mock_hass():
    """Mock HomeAssistant instance with a mocked data and bus attribute."""
    mock_hass_instance = MagicMock(spec=HomeAssistant)
    mock_hass_instance.data = {}  # Initialize as an empty dictionary
    # Mock the bus attribute with a MagicMock
    mock_hass_instance.bus = MagicMock()
    # Mock the config_entries attribute to have async_unload_platforms
    mock_hass_instance.config_entries.async_unload_platforms = AsyncMock(
        return_value=True
    )
    return mock_hass_instance


@pytest.fixture
def mock_entry():
    """Mock ConfigEntry."""
    return MagicMock(spec=ConfigEntry)


@pytest.fixture
def mock_async_get_clientsession():
    """Mock the async_get_clientsession function."""
    return MagicMock(return_value=AsyncMock())


@pytest.fixture
def mock_nasa_api_client():
    """Mock the NasaApiClient."""
    return MagicMock(NasaApiClient)


@pytest.fixture
def mock_nasa_coordinator():
    """Mock the NasaDataUpdateCoordinator."""
    return MagicMock(NasaDataUpdateCoordinator)


@pytest.mark.asyncio
async def test_async_unload_entry(mock_hass, mock_entry, mock_nasa_coordinator) -> None:
    """Test the async_unload_entry function."""

    # Arrange
    mock_entry.entry_id = "test_entry_id"
    mock_hass.data[DOMAIN] = {mock_entry.entry_id: mock_nasa_coordinator}

    # Mock unloading behavior
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    # Call the function
    result = await async_unload_entry(mock_hass, mock_entry)

    # Assertions
    assert result is True
    mock_hass.config_entries.async_unload_platforms.assert_called_once_with(
        mock_entry, ["image", "sensor"]
    )
    mock_hass.data[DOMAIN].pop(mock_entry.entry_id, None)
    assert mock_entry.entry_id not in mock_hass.data[DOMAIN]
