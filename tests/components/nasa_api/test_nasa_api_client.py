"""Unit tests for the NASA API client integration."""

from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp import ClientResponseError, ClientSession, RequestInfo
import pytest
from yarl import URL

from homeassistant.components.nasa_api.const import DEFAULT_API_KEY
from homeassistant.components.nasa_api.models import ApodImage, MarsWeather
from homeassistant.components.nasa_api.nasa_api_client import NasaApiClient


def test_initialization_with_api_key() -> None:
    """Test initialization with a provided API key."""
    session = MagicMock(spec=ClientSession)
    client = NasaApiClient(api_key="test_api_key", session=session)

    assert client.api_key == "test_api_key", "Client should use the provided API key"
    assert client.session == session, "Client should use the provided session"


def test_initialization_with_default_api_key() -> None:
    """Test initialization with no API key (uses default)."""
    session = MagicMock(spec=ClientSession)
    client = NasaApiClient(api_key=None, session=session)

    assert (
        client.api_key == DEFAULT_API_KEY
    ), "Client should use the default API key when none is provided"
    assert client.session == session, "Client should use the provided session"


# Test http error
@pytest.mark.asyncio
async def test_fetch_neos_data_http_error() -> None:
    """Test that the client handles HTTP errors gracefully."""

    # Mock `ClientResponseError`
    request_info = RequestInfo(url=URL("https://example.com"), method="GET", headers={})
    error = ClientResponseError(
        request_info=request_info,
        history=(),
        status=500,
        message="Internal Server Error",
    )

    with patch("aiohttp.ClientSession.get") as mock_get:
        # Simulate the `get` method raising a ClientResponseError
        mock_get.side_effect = error

        # Initialize the client
        async with ClientSession() as session:
            client = NasaApiClient("test_api_key", session)

            # Call the method to fetch NEO data
            result = await client.fetch_neos_data()

            # Verify the result
            assert result == [], "Should return an empty list on HTTP error"


@pytest.mark.asyncio
async def test_fetch_apod_data_successful() -> None:
    """Test fetching APOD data successfully."""
    apod_response = {
        "date": "2024-11-01",
        "explanation": "Sample explanation",
        "hdurl": "https://example.com/hd.jpg",
        "media_type": "image",
        "title": "Sample Title",
        "url": "https://example.com.jpg",
    }

    mock_response = AsyncMock()
    mock_response.json.return_value = apod_response
    mock_response.__aenter__.return_value = mock_response
    mock_response.__aexit__.return_value = None

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        async with ClientSession() as session:
            client = NasaApiClient("test_api_key", session)
            result = await client.fetch_apod_data()

            assert isinstance(result, ApodImage), "Result should be an ApodImage object"
            assert result.title == "Sample Title"
            assert result.media_type == "image"


@pytest.mark.asyncio
async def test_fetch_apod_data_http_error() -> None:
    """Test that APOD data fetch handles HTTP errors gracefully."""
    request_info = RequestInfo(url=URL("https://example.com"), method="GET", headers={})
    error = ClientResponseError(
        request_info=request_info,
        history=(),
        status=500,
        message="Internal Server Error",
    )

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.side_effect = error

        async with ClientSession() as session:
            client = NasaApiClient("test_api_key", session)
            with pytest.raises(ClientResponseError):
                await client.fetch_apod_data()


@pytest.mark.asyncio
async def test_fetch_mars_weather_successful() -> None:
    """Test fetching Mars weather data successfully."""
    mars_weather_response = {
        "sol_keys": ["123", "124"],
        "123": {
            "AT": {"av": -60, "mn": -95, "mx": -25},
            "PRE": {"av": 700},
            "HWS": {"av": 10},
            "WD": {"most_common": {"compass_degrees": 270}},
            "Season": "Summer",
        },
        "124": {
            "AT": {"av": -62, "mn": -97, "mx": -30},
            "PRE": {"av": 710},
            "HWS": {"av": 12},
            "WD": {"most_common": {"compass_degrees": 280}},
            "Season": "Fall",
        },
    }

    mock_response = AsyncMock()
    mock_response.json.return_value = mars_weather_response
    mock_response.__aenter__.return_value = mock_response
    mock_response.__aexit__.return_value = None

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        async with ClientSession() as session:
            client = NasaApiClient("test_api_key", session)
            result = await client.fetch_mars_weather()

            assert isinstance(result, list), "Result should be a list"
            assert len(result) == 2, "Result should contain two sol weather objects"
            assert isinstance(
                result[0], MarsWeather
            ), "Result should contain MarsWeather objects"
            assert result[0].sol == "123"
            assert result[0].temperature == -60


@pytest.mark.asyncio
async def test_fetch_mars_weather_http_error() -> None:
    """Test that Mars weather fetch handles HTTP errors gracefully."""
    request_info = RequestInfo(url=URL("https://example.com"), method="GET", headers={})
    error = ClientResponseError(
        request_info=request_info,
        history=(),
        status=500,
        message="Internal Server Error",
    )

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.side_effect = error

        async with ClientSession() as session:
            client = NasaApiClient("test_api_key", session)
            with pytest.raises(ClientResponseError):
                await client.fetch_mars_weather()
