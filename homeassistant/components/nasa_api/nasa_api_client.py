"""NASA API Client."""

from __future__ import annotations

from datetime import datetime
import json

from aiohttp import ClientResponseError, ClientSession

from .const import DEFAULT_API_KEY, LOGGER
from .models import NeoWsAsteroid

API_URL = "https://api.nasa.gov/neo/rest/v1/feed"


class NasaApiClient:
    """NASA API Client to fetch NEO data."""

    def __init__(self, api_key: str, session: ClientSession) -> None:
        """Initialize the client with API key and session."""
        self.api_key = api_key or DEFAULT_API_KEY
        self.session = session

    async def fetch_neos_data(self) -> list[NeoWsAsteroid]:
        """Fetch NEO data for the current day and log the response data."""
        # Generate today's date in YYYY-MM-DD format
        today = datetime.now().strftime("%Y-%m-%d")
        params = {
            "start_date": today,
            "end_date": today,
            "api_key": self.api_key,
        }

        try:
            async with self.session.get(API_URL, params=params) as response:
                response.raise_for_status()  # Raise exception for HTTP errors
                data = await response.json()  # Parse JSON response
                # Extract asteroids from the data
                asteroid_data = data["near_earth_objects"].get(today, [])
                # Convert each asteroid dictionary to a NeoWsAsteroid object
                return [NeoWsAsteroid.from_dict(asteroid) for asteroid in asteroid_data]
        except ClientResponseError as e:
            LOGGER.error("HTTP error fetching NEO data: %s", e)
        except json.JSONDecodeError as e:
            LOGGER.error("JSON parsing error fetching NEO data: %s", e)
        except Exception as e:  # This will catch any other unexpected exceptions
            LOGGER.error("Unexpected error fetching NEO data: %s", e)
            raise  # Re-raise the exception to propagate the error
        return []
