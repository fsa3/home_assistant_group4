"""NASA API Client."""

from __future__ import annotations

from datetime import datetime
import json

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import DEFAULT_API_KEY, INSIGHT_PARAMS, LOGGER
from .models import ApodImage, MarsWeather, NeoWsAsteroid, parse_mars_weather

API_URL = "https://api.nasa.gov/"


class NasaApiClient:
    """NASA API Client to fetch NEO data."""

    def __init__(self, api_key: str, session: ClientSession) -> None:
        """Initialize the client with API key and session."""
        self.api_key = api_key or DEFAULT_API_KEY
        self.session = session

    async def validate_api_key(self, api_key) -> bool:
        """Validate the API key by making a simple request to the APOD endpoint."""
        params = {
            "api_key": api_key,
        }

        try:
            async with self.session.get(
                API_URL + "planetary/apod", params=params
            ) as response:
                response.raise_for_status()
                # Key valid if the request is successful
                return True
        except ClientResponseError as e:
            if e.status in (403, 401):
                LOGGER.error("Invalid API key: %s", e)
            else:
                LOGGER.error("HTTP error during API key validation: %s", e)
        except (TimeoutError, ClientError) as e:
            LOGGER.error("Unexpected error during API key validation: %s", e)

        # return False (invalid key)
        return False

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
            async with self.session.get(
                API_URL + "neo/rest/v1/feed", params=params
            ) as response:
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
        except (
            TimeoutError,
            ClientError,
        ) as e:
            LOGGER.error("Unexpected error fetching NEO data: %s", e)
            raise
        return []

    async def fetch_apod_data(self) -> ApodImage:
        """Fetch Astronomy Picture of the Day (APOD) data."""
        params = {
            "api_key": self.api_key,
        }

        try:
            async with self.session.get(
                API_URL + "planetary/apod", params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return ApodImage.from_dict(data)
        except ClientResponseError as e:
            LOGGER.error("HTTP error fetching APOD data: %s", e)
            raise
        except json.JSONDecodeError as e:
            LOGGER.error("JSON parsing error fetching APOD data: %s", e)
            raise
        except Exception as e:
            LOGGER.error("Unexpected error fetching APOD data: %s", e)
            raise

    async def fetch_mars_weather(self) -> list[MarsWeather]:
        """Fetch Mars weather data from the InSight API."""
        params = {"api_key": self.api_key, **INSIGHT_PARAMS}

        try:
            async with self.session.get(
                API_URL + "insight_weather/", params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                mars_weather = parse_mars_weather(data)
                LOGGER.debug("Successfully fetched and parsed Mars weather data")
                return mars_weather
        except ClientResponseError as e:
            LOGGER.error("HTTP error fetching Mars weather data: %s", e)
            raise
        except json.JSONDecodeError as e:
            LOGGER.error("JSON parsing error fetching Mars weather data: %s", e)
            raise
        except Exception as e:
            LOGGER.error("Unexpected error fetching Mars weather data: %s", e)
            raise
