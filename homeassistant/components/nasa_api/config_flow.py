"""Config flow for NASA API integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_API_KEY, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NASAConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NASA API."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self.data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input.get(CONF_API_KEY, DEFAULT_API_KEY)
            # session = async_get_clientsession(self.hass)

            # validate the API key here
            _LOGGER.debug("NASA API key: %s", api_key)

            self.data = user_input

            return self.async_create_entry(
                title="NASA API",
                data={CONF_API_KEY: api_key},
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY, default=DEFAULT_API_KEY): str,
            }
        )

        # Display form to user
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
