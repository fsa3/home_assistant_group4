"""Test file for weather.py in the NASA API components."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.components.nasa_api.const import (
    CONF_DATA_SOURCES,
    DATA_SOURCE_INSIGHT,
    DOMAIN,
)
from homeassistant.components.nasa_api.models import MarsWeather
from homeassistant.components.nasa_api.weather import (
    MarsWeatherEntity,
    async_setup_entry,
)
from homeassistant.core import HomeAssistant


# Mock Coordinator
@pytest.fixture
def mock_coordinator() -> MagicMock:
    """Create a mock coordinator with sample Mars weather data."""
    return MagicMock(
        data={
            DATA_SOURCE_INSIGHT: [
                MarsWeather(
                    sol="1000",
                    temperature=-60.0,
                    temperature_min=-90.0,
                    temperature_max=-30.0,
                    pressure=720.5,
                    wind_speed=5.2,
                    wind_bearing=270.0,
                    season="winter",
                    first_utc="2024-01-01T00:00:00Z",
                    last_utc="2024-01-02T00:00:00Z",
                    humidity=10.5,
                )
            ]
        }
    )


# Test 1: Entity Setup
@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant, mock_coordinator) -> None:
    """Test setting up the Mars Weather entity."""
    # Case 1: Mock ConfigEntry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {CONF_DATA_SOURCES: [DATA_SOURCE_INSIGHT]}  # Enable InSight source

    # Case 2: Inject mock coordinator into Home Assistant data
    hass.data = {DOMAIN: {entry.entry_id: mock_coordinator}}

    # Case 3: Mock async_add_entities, provide mock data
    async_add_entities = AsyncMock()
    mock_coordinator.sources = [DATA_SOURCE_INSIGHT]

    # Act: Call async_setup_entry
    await async_setup_entry(hass, entry, async_add_entities)

    # Assert: Verify that the entity was added
    async_add_entities.assert_called_once()
    added_entities = async_add_entities.call_args[0][0]
    assert len(added_entities) == 1
    entity = added_entities[0]
    assert isinstance(entity, MarsWeatherEntity)
    assert entity.name == "Mars Weather"


# Test 2: Temperature Properties
def test_temperature_properties(mock_coordinator) -> None:
    """Test the native_temperature property of the MarsWeatherEntity."""
    # Case 1: Valid temperature data
    entity = MarsWeatherEntity(mock_coordinator)
    assert entity.native_temperature == -60.0, "Expected temperature to match mock data"


# Test 3: Wind Properties
def test_wind_properties(mock_coordinator) -> None:
    """Test wind_speed and wind_bearing properties."""
    # Case 1: Valid wind data
    entity = MarsWeatherEntity(mock_coordinator)
    assert entity.native_wind_speed == 5.2, "Expected wind speed to match mock data"

    # Case 2: Verify wind bearing in extra_state_attributes
    assert (
        entity.extra_state_attributes["wind_bearing"] == 270.0
    ), "Expected wind bearing to match mock data"


# Test 4: Entity Metadata
def test_entity_metadata(mock_coordinator) -> None:
    """Test entity name and unique_id properties of the MarsWeatherEntity."""
    # Case 1: Validate metadata
    entity = MarsWeatherEntity(mock_coordinator)
    assert entity.name == "Mars Weather"
    assert entity.unique_id == f"{DOMAIN}_mars_weather"
