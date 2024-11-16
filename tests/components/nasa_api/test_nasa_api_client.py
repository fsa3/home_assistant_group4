"""Unit tests for the NASA API client integration."""

from unittest.mock import MagicMock, patch

from aiohttp import ClientResponseError, ClientSession, RequestInfo
import pytest
from yarl import URL

from homeassistant.components.nasa_api.const import DEFAULT_API_KEY
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
    request_info = RequestInfo(url=URL("http://example.com"), method="GET", headers={})
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

            # You can also verify if the error is logged (optional)


# Test Json Parsiing error
