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
DATA_SOURCES = [
    DATA_SOURCE_NEOWS,
    DATA_SOURCE_APOD,
]

DATA_SOURCE_FRIENDLY_NAMES = {
    DATA_SOURCE_NEOWS: "Near-Earth Objects (NEOWS)",
    DATA_SOURCE_APOD: "Astronomy Picture of the Day (APOD)",
}
