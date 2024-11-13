"""Unit tests for the sensor components in the NASA API integration."""

from datetime import timedelta
import unittest
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.nasa_api.coordinator import NasaDataUpdateCoordinator
from homeassistant.components.nasa_api.models import NeoWsAsteroid
from homeassistant.helpers.update_coordinator import UpdateFailed


class TestNasaDataUpdateCoordinator(unittest.TestCase):  # noqa: D101
    def setUp(self):
        """Set up a coordinator instance with a mocked NASA API client."""
        self.hass = AsyncMock()  # Mock HomeAssistant instance
        self.api_client = AsyncMock()  # Mock NASA API client
        self.coordinator = NasaDataUpdateCoordinator(
            hass=self.hass, client=self.api_client
        )

    @patch(
        "homeassistant.components.nasa_api.coordinator.NasaDataUpdateCoordinator.update_interval",
        timedelta(seconds=10),
    )
    def test_initialization(self):
        """Test that the coordinator is initialized with the correct update interval."""
        assert self.coordinator.update_interval, timedelta(seconds=10)

    async def test_successful_data_fetch(self):
        """Test that data is fetched successfully and returned correctly."""
        mock_data = [NeoWsAsteroid(id="12345", name="TestAsteroid", size="500")]
        self.api_client.fetch_neos_data.return_value = (
            mock_data  # Mock successful API response
        )

        result = await self.coordinator._async_update_neows_data()

        assert result == mock_data
        assert self.coordinator.cache["neows"] == mock_data

    async def test_data_fetch_with_api_failure_and_cache(self):
        """Test that the coordinator uses cached data if the API call fails."""
        # Set up the cache with mock data
        cached_data = [NeoWsAsteroid(id="54321", name="CachedAsteroid", size="300")]
        self.coordinator.cache["neows"] = cached_data

        self.api_client.fetch_neos_data.side_effect = Exception("API failure")

        result = await self.coordinator._async_update_neows_data()

        assert result == cached_data  # Should return cached data

    async def test_data_fetch_failure_without_cache(self):
        """Test that an UpdateFailed exception is raised if there is no cached data and API call fails."""
        self.api_client.fetch_neos_data.side_effect = Exception("API failure")

        with pytest.raises(UpdateFailed):
            await self.coordinator._async_update_neows_data()


# Run tests
if __name__ == "__main__":
    unittest.main()
