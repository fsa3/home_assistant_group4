"""Unit tests for the sensor components in the NASA API integration."""

from datetime import timedelta
import unittest
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.nasa_api.const import (
    DATA_SOURCE_APOD,
    DATA_SOURCE_INSIGHT,
    DATA_SOURCE_NEOWS,
    DATA_SOURCES,
)
from homeassistant.components.nasa_api.coordinator import NasaDataUpdateCoordinator
from homeassistant.components.nasa_api.models import ApodImage, NeoWsAsteroid
from homeassistant.helpers.update_coordinator import UpdateFailed


class TestNasaDataUpdateCoordinator(unittest.TestCase):  # noqa: D101
    def setUp(self):
        """Set up a coordinator instance with a mocked NASA API client."""
        self.hass = AsyncMock()  # Mock HomeAssistant instance
        self.api_client = AsyncMock()  # Mock NASA API client
        self.coordinator = NasaDataUpdateCoordinator(
            hass=self.hass, client=self.api_client, sources=DATA_SOURCES
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
        assert self.coordinator.cache[DATA_SOURCE_NEOWS] == mock_data

    async def test_data_fetch_with_api_failure_and_cache(self):
        """Test that the coordinator uses cached data if the API call fails."""
        # Set up the cache with mock data
        cached_data = [NeoWsAsteroid(id="54321", name="CachedAsteroid", size="300")]
        self.coordinator.cache[DATA_SOURCE_NEOWS] = cached_data

        self.api_client.fetch_neos_data.side_effect = Exception("API failure")

        result = await self.coordinator._async_update_neows_data()

        assert result == cached_data  # Should return cached data

    async def test_data_fetch_failure_without_cache(self):
        """Test that an UpdateFailed exception is raised if there is no cached data and API call fails."""
        self.api_client.fetch_neos_data.side_effect = Exception("API failure")

        with pytest.raises(UpdateFailed):
            await self.coordinator._async_update_neows_data()

    async def test_async_update_apod_data(self):
        """Test _async_update_apod_data with valid data."""
        # Mock valid APOD data
        mock_apod_data = ApodImage(
            url="https://example.com/image.jpg",
            title="Test APOD Image",
            explanation="This is a test explanation for APOD.",
            date="2024-01-01",
            hdurl="https://example.com/hd_image.jpg",
            media_type="image",
        )
        self.api_client.fetch_apod_data.return_value = mock_apod_data

        # Call the method
        result = await self.coordinator._async_update_apod_data()

        # Verify the result
        assert result == mock_apod_data
        assert self.coordinator.cache[DATA_SOURCE_APOD] == mock_apod_data

        async def test_async_update_apod_data_invalid_media_type(self):
            """Test _async_update_apod_data with invalid media type."""
            # Mock invalid APOD data with a non-image media type
            mock_apod_data = ApodImage(
                url="https://example.com/video.mp4",
                title="Test Video",
                explanation="This is a test explanation for APOD.",
                date="2024-01-01",
                hdurl="https://example.com/video_hd.mp4",
                media_type="video",
            )
            self.api_client.fetch_apod_data.return_value = mock_apod_data

            # Call the method
            with pytest.raises(UpdateFailed):
                await self.coordinator._async_update_apod_data()

        async def test_async_update_apod_data_cache_fallback(self):
            """Test _async_update_apod_data falls back to cached data on API failure."""
            # Populate cache with mock data
            cached_apod_data = ApodImage(
                url="https://example.com/cached_image.jpg",
                title="Cached Image",
                explanation="This is cached APOD data.",
                date="2023-12-31",
                hdurl="https://example.com/cached_hd_image.jpg",
                media_type="image",
            )
            self.coordinator.cache[DATA_SOURCE_APOD] = cached_apod_data

            # Simulate API failure
            self.api_client.fetch_apod_data.side_effect = Exception("API failure")

            # Call the method
            result = await self.coordinator._async_update_apod_data()

            # Verify that cached data is returned
            assert result == cached_apod_data

        async def test_async_update_insight_data(self):
            """Test _async_update_insight_data with valid data."""
            # Mock valid Mars weather data
            mock_insight_data = [
                {"sol": "1001", "temperature": "20C"},
                {"sol": "1002", "temperature": "18C"},
            ]
            self.api_client.fetch_mars_weather.return_value = mock_insight_data

            # Call the method
            result = await self.coordinator._async_update_insight_data()

            # Verify the result
            assert result == mock_insight_data
            assert self.coordinator.cache[DATA_SOURCE_INSIGHT] == mock_insight_data

        async def test_async_update_insight_data_empty_data(self):
            """Test _async_update_insight_data with empty data."""
            # Mock empty Mars weather data
            self.api_client.fetch_mars_weather.return_value = []

            # Call the method
            result = await self.coordinator._async_update_insight_data()

            # Verify the result is empty
            assert result == []
            assert self.coordinator.cache.get(DATA_SOURCE_INSIGHT) == []

        async def test_async_update_insight_data_cache_fallback(self):
            """Test _async_update_insight_data falls back to cached data on API failure."""
            # Populate cache with mock data
            cached_insight_data = [
                {"sol": "999", "temperature": "15C"},
                {"sol": "1000", "temperature": "17C"},
            ]
            self.coordinator.cache[DATA_SOURCE_INSIGHT] = cached_insight_data

            # Simulate API failure
            self.api_client.fetch_mars_weather.side_effect = Exception("API failure")

            # Call the method
            result = await self.coordinator._async_update_insight_data()

            # Verify that cached data is returned
            assert result == cached_insight_data


# Run tests
if __name__ == "__main__":
    unittest.main()
