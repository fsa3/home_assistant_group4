"""Test the NASA API config flow."""

from unittest.mock import patch

import pytest

from homeassistant import config_entries
from homeassistant.components.nasa_api.const import DOMAIN
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

# Mock key for testing
MOCK_API_KEY = "test-api-key"


async def test_form_success(hass: HomeAssistant) -> None:
    """Test the config flow form successfully creates an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.nasa_api.nasa_api_client.NasaApiClient.validate_api_key",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: MOCK_API_KEY}
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "NASA API"
    assert result["data"] == {CONF_API_KEY: MOCK_API_KEY}


async def test_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test we handle invalid API key during the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.nasa_api.nasa_api_client.NasaApiClient.validate_api_key",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: MOCK_API_KEY}
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_form_exception(hass: HomeAssistant) -> None:
    """Test we handle an unexpected exception during API key validation."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with (
        patch(
            "homeassistant.components.nasa_api.nasa_api_client.NasaApiClient.validate_api_key",
            side_effect=Exception("Unexpected error"),
        ),
        pytest.raises(Exception, match="Unexpected error"),
    ):
        await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: MOCK_API_KEY}
        )
