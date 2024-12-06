"""Config flow for NASA API integration."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_DATA_SOURCES,
    DATA_SOURCE_FRIENDLY_NAMES,
    DEFAULT_API_KEY,
    DOMAIN,
)
from .nasa_api_client import NasaApiClient

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
        """Handle the initial step to enter the API key."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input.get(CONF_API_KEY, DEFAULT_API_KEY)
            session = async_get_clientsession(self.hass)

            _LOGGER.debug("NASA API key: %s", api_key)

            api_client = NasaApiClient(api_key, session)

            try:
                api_key_valid = await api_client.validate_api_key(api_key)
            except (ClientError, TimeoutError) as e:
                _LOGGER.error("Network error during API key validation: %s", e)
                errors["base"] = "cannot_connect"
            except ValueError as e:
                _LOGGER.error("Value error during API key validation: %s", e)
                errors["base"] = "invalid_response"
            except Exception as e:
                _LOGGER.error("Unexpected error during API key validation: %s", e)
                raise
            else:
                if not api_key_valid:
                    errors["base"] = "invalid_auth"
                    _LOGGER.error("Invalid NASA API key provided by user")
                else:
                    _LOGGER.debug("Valid NASA API key: %s", api_key)
                    self.data[CONF_API_KEY] = api_key

                    # Move to the next step
                    return await self.async_step_data_sources()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY, default=DEFAULT_API_KEY): str,
            }
        )

        # Display form to user
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_data_sources(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the data source selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_sources = user_input.get(CONF_DATA_SOURCES, [])
            if not selected_sources:
                errors["base"] = "no_data_source_selection"
            else:
                self.data[CONF_DATA_SOURCES] = selected_sources

                return self.async_create_entry(
                    title="NASA API",
                    data=self.data,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_DATA_SOURCES, default=[]): cv.multi_select(
                    DATA_SOURCE_FRIENDLY_NAMES
                ),
            }
        )

        # Display form to user
        return self.async_show_form(
            step_id="data_sources", data_schema=data_schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
