"""Constants for the NASA API integration."""

import logging

DOMAIN = "nasa_api"
LOGGER = logging.getLogger(__package__)

CONF_API_KEY = "api_key"
CONF_DATA_SOURCES = "nasa_data_sources"

DEFAULT_API_KEY = "DEMO_KEY"

# Data sources
DATA_SOURCE_NEOWS = "neows"
DATA_SOURCE_APOD = "apod"
DATA_SOURCE_INSIGHT = "insight"
DATA_SOURCES = [
    DATA_SOURCE_NEOWS,
    DATA_SOURCE_APOD,
    DATA_SOURCE_INSIGHT,
]

DATA_SOURCE_FRIENDLY_NAMES = {
    DATA_SOURCE_NEOWS: "Near-Earth Objects (NEOWS)",
    DATA_SOURCE_APOD: "Astronomy Picture of the Day (APOD)",
    DATA_SOURCE_INSIGHT: "Mars Weather (InSight)",
}

# InSight Mars Weather API
INSIGHT_API_URL = "https://api.nasa.gov/insight_weather/"
INSIGHT_PARAMS = {"feedtype": "json", "ver": "1.0"}
INSIGHT_UPDATE_INTERVAL = 3600  # 1 hour in seconds

# Default values for Mars Weather
MARS_WEATHER_NAME = "Mars Weather"
UNIT_TEMPERATURE = "°C"
UNIT_PRESSURE = "Pa"
UNIT_WIND_SPEED = "m/s"
