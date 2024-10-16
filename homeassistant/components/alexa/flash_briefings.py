"""Support for Alexa skill service end point."""

import hmac
from http import HTTPStatus
import logging
import uuid

from aiohttp.web_response import StreamResponse

from homeassistant.components import http
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import template
from homeassistant.helpers.typing import ConfigType
import homeassistant.util.dt as dt_util

from .const import (
    API_PASSWORD,
    ATTR_MAIN_TEXT,
    ATTR_REDIRECTION_URL,
    ATTR_STREAM_URL,
    ATTR_TITLE_TEXT,
    ATTR_UID,
    ATTR_UPDATE_DATE,
    CONF_AUDIO,
    CONF_DISPLAY_URL,
    CONF_TEXT,
    CONF_TITLE,
    CONF_UID,
    DATE_FORMAT,
)

_LOGGER = logging.getLogger(__name__)

FLASH_BRIEFINGS_API_ENDPOINT = "/api/alexa/flash_briefings/{briefing_id}"


@callback
def async_setup(hass: HomeAssistant, flash_briefing_config: ConfigType) -> None:
    """Activate Alexa component."""
    hass.http.register_view(AlexaFlashBriefingView(hass, flash_briefing_config))


class AlexaFlashBriefingView(http.HomeAssistantView):
    """Handle Alexa Flash Briefing skill requests."""

    url = FLASH_BRIEFINGS_API_ENDPOINT
    requires_auth = False
    name = "api:alexa:flash_briefings"

    def __init__(self, hass: HomeAssistant, flash_briefings: ConfigType) -> None:
        """Initialize Alexa view."""
        super().__init__()
        self.flash_briefings = flash_briefings

    @callback
    @callback
    def get(
        self, request: http.HomeAssistantRequest, briefing_id: str
    ) -> StreamResponse | tuple[bytes, HTTPStatus]:
        """Handle Alexa Flash Briefing request."""
        _LOGGER.debug("Received Alexa flash briefing request for: %s", briefing_id)

        # Validate request password
        if not self.validate_password(request):
            return b"", HTTPStatus.UNAUTHORIZED

        # Validate briefing ID
        if not self.is_valid_briefing(briefing_id):
            return b"", HTTPStatus.NOT_FOUND

        briefing = []
        for item in self.flash_briefings.get(briefing_id, []):
            output = self.process_item(item)
            if output:
                briefing.append(output)

        return self.json(briefing)

    def validate_password(self, request: http.HomeAssistantRequest) -> bool:
        """Validate the password provided in the request."""
        if request.query.get(API_PASSWORD) is None:
            _LOGGER.error("No password provided for Alexa flash briefing")
            return False

        if not hmac.compare_digest(
            request.query[API_PASSWORD].encode("utf-8"),
            self.flash_briefings[CONF_PASSWORD].encode("utf-8"),
        ):
            _LOGGER.error("Wrong password for Alexa flash briefing")
            return False

        return True

    def is_valid_briefing(self, briefing_id: str) -> bool:
        """Check if the briefing ID is valid."""
        if not isinstance(self.flash_briefings.get(briefing_id), list):
            _LOGGER.error(
                "No configured Alexa flash briefing was found for: %s", briefing_id
            )
            return False
        return True

    def process_item(self, item: dict) -> dict[str, str]:
        """Process a single flash briefing item and return its output."""
        output: dict[str, str] = {}

        self.add_attribute_to_output(item, CONF_TITLE, output, ATTR_TITLE_TEXT)
        self.add_attribute_to_output(item, CONF_TEXT, output, ATTR_MAIN_TEXT)

        uid = self.get_uid(item)
        output[ATTR_UID] = uid

        self.add_attribute_to_output(item, CONF_AUDIO, output, ATTR_STREAM_URL)
        self.add_attribute_to_output(
            item, CONF_DISPLAY_URL, output, ATTR_REDIRECTION_URL
        )

        output[ATTR_UPDATE_DATE] = dt_util.utcnow().strftime(DATE_FORMAT)

        return output

    def add_attribute_to_output(
        self, item: dict, conf_key: str, output: dict, output_key: str
    ) -> None:
        """Add an attribute to the output based on its configuration key."""
        if item.get(conf_key) is not None:
            if isinstance(item[conf_key], template.Template):
                output[output_key] = item[conf_key].async_render(parse_result=False)
            else:
                output[output_key] = item.get(conf_key)

    def get_uid(self, item: dict) -> str:
        """Get or generate a UID for the item."""
        if (uid := item.get(CONF_UID)) is None:
            return str(uuid.uuid4())
        return str(uid)
