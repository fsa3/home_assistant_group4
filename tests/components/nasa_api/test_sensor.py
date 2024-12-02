"""Unittests for sensor.py in components/nasa_api."""

import math
from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.components.nasa_api.const import (
    CONF_DATA_SOURCES,
    DATA_SOURCE_NEOWS,
    DOMAIN,
)
from homeassistant.components.nasa_api.coordinator import NasaDataUpdateCoordinator
from homeassistant.components.nasa_api.models import (
    CloseApproachData,
    EstimatedDiameter,
    NeoWsAsteroid,
)
from homeassistant.components.nasa_api.sensor import (
    SUMMARY_SENSOR_DESCRIPTIONS,
    NasaNeoSummarySensor,
    async_setup_entry,
)


# 1. Test Adding Sensors (async_setup_entry)
@pytest.mark.asyncio
async def test_async_setup_entry() -> None:
    """Test that sensors are correctly added when NEOWS data source is enabled."""
    # Mock the HomeAssistant object
    hass = MagicMock()

    # Mock the ConfigEntry object
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {CONF_DATA_SOURCES: [DATA_SOURCE_NEOWS]}  # Ensure NEOWS is enabled

    # Mock the coordinator with dummy data
    mock_coordinator = MagicMock(spec=NasaDataUpdateCoordinator)
    mock_coordinator.data = {DATA_SOURCE_NEOWS: []}  # Example empty data for setup
    hass.data = {DOMAIN: {entry.entry_id: mock_coordinator}}

    # Mock the async_add_entities callback
    async_add_entities = AsyncMock()

    # Call the async_setup_entry function
    await async_setup_entry(hass, entry, async_add_entities)

    # Verify async_add_entities is called once
    async_add_entities.assert_called_once()

    # Verify the correct number of sensors are added
    added_entities = async_add_entities.call_args[0][0]
    assert len(added_entities) == len(
        SUMMARY_SENSOR_DESCRIPTIONS
    ), f"Expected {len(SUMMARY_SENSOR_DESCRIPTIONS)} sensors, "


# 2. Test Native Value for Each Sensor


@pytest.fixture
def mock_coordinator() -> None:
    """Create a mock coordinator with sample NEO data."""
    return MagicMock(
        data={
            DATA_SOURCE_NEOWS: [
                NeoWsAsteroid(
                    id="1",
                    name="Asteroid 1",
                    nasa_jpl_url="https://example.com/asteroid1",
                    absolute_magnitude_h=22.5,
                    estimated_diameter=EstimatedDiameter(
                        min_km=0.5,
                        max_km=1.5,
                        min_meters=500,
                        max_meters=1500,
                        min_miles=0.3,
                        max_miles=0.9,
                        min_feet=1640.42,
                        max_feet=4921.26,
                    ),
                    is_potentially_hazardous=True,
                    close_approach_data=[
                        CloseApproachData(
                            close_approach_date="2024-01-01",
                            close_approach_date_full="2024-Jan-01 00:00",
                            epoch_date_close_approach=1704067200000,
                            miss_distance_km=35000,
                            miss_distance_miles=21748,
                            miss_distance_au=0.000234,
                            miss_distance_lunar=0.09,
                            relative_velocity_kph=25000,
                            relative_velocity_mph=15534,
                            relative_velocity_kps=6.94,
                            orbiting_body="Earth",
                        )
                    ],
                    is_sentry_object=False,
                    sentry_data_url=None,
                ),
                NeoWsAsteroid(
                    id="2",
                    name="Asteroid 2",
                    nasa_jpl_url="https://example.com/asteroid2",
                    absolute_magnitude_h=23.2,
                    estimated_diameter=EstimatedDiameter(
                        min_km=0.2,
                        max_km=0.6,
                        min_meters=200,
                        max_meters=600,
                        min_miles=0.12,
                        max_miles=0.37,
                        min_feet=656.17,
                        max_feet=1968.5,
                    ),
                    is_potentially_hazardous=False,
                    close_approach_data=[
                        CloseApproachData(
                            close_approach_date="2024-02-01",
                            close_approach_date_full="2024-Feb-01 00:00",
                            epoch_date_close_approach=1706745600000,
                            miss_distance_km=500000,
                            miss_distance_miles=310685,
                            miss_distance_au=0.00334,
                            miss_distance_lunar=1.29,
                            relative_velocity_kph=15000,
                            relative_velocity_mph=9320,
                            relative_velocity_kps=4.17,
                            orbiting_body="Earth",
                        )
                    ],
                    is_sentry_object=True,
                    sentry_data_url="https://example.com/sentry2",
                ),
            ]
        }
    )


def test_native_value(mock_coordinator) -> None:
    """Test the native_value calculation for all sensor types."""
    # Define expected values for each sensor
    expected_values = {
        "total_neo_count": 2,  # Two asteroids in mock data
        "hazardous_count": 1,  # One hazardous asteroid
        "largest_diameter_meter": 1500,  # Asteroid 1 has the largest max diameter
        "smallest_diameter_meter": 200,  # Asteroid 2 has the smallest min diameter
        "average_diameter_meter": 700,  # (1.5+0.5 + 0.6+0.2) / (2*2)
        "closest_approach_km": 35000,  # Closest approach is Asteroid 1
        "farthest_approach_km": 500000,  # Farthest approach is Asteroid 2
        "fastest_velocity_kph": 25000,  # Asteroid 1 is faster
        "slowest_velocity_kph": 15000,  # Asteroid 2 is slower
    }

    # Test each sensor
    for description in SUMMARY_SENSOR_DESCRIPTIONS:
        sensor = NasaNeoSummarySensor(mock_coordinator, description)

        # Verify the native_value for each sensor
        expected = expected_values[description.key]
        assert (
            sensor.native_value == expected
        ), f"Failed for sensor key: {description.key}"


def test_native_value_no_data() -> None:
    """Test native_value behavior when no data is available."""
    mock_coordinator = MagicMock(data={DATA_SOURCE_NEOWS: []})  # No asteroid data
    for description in SUMMARY_SENSOR_DESCRIPTIONS:
        sensor = NasaNeoSummarySensor(mock_coordinator, description)
        assert (
            sensor.native_value is None
        ), f"Failed for sensor key: {description.key} with no data"


# 3. Test Extra State Attributes
def test_extra_state_attributes(mock_coordinator) -> None:
    """Test that extra_state_attributes returns detailed asteroid data."""
    # Use the first sensor description for testing
    description = SUMMARY_SENSOR_DESCRIPTIONS[0]
    sensor = NasaNeoSummarySensor(mock_coordinator, description)

    # Get the extra_state_attributes
    attributes = sensor.extra_state_attributes

    # Verify the attributes contain data for each asteroid
    assert "asteroids" in attributes

    # Verify details for Asteroid 1
    asteroid_1_attrs = attributes["asteroids"][0]
    assert asteroid_1_attrs["id"] == "1"
    assert math.isclose(
        asteroid_1_attrs["diameter_m"], 1500, rel_tol=1e-9
    )  # Largest diameter
    assert asteroid_1_attrs["hazardous"] == "Yes"
    assert asteroid_1_attrs["close_approach_date"] == "2024-Jan-01 00:00"
    assert asteroid_1_attrs["miss_distance_km"] == 35000
    assert asteroid_1_attrs["relative_velocity_kph"] == 25000

    # Verify details for Asteroid 2
    asteroid_2_attrs = attributes["asteroids"][1]
    assert asteroid_2_attrs["id"] == "2"
    assert math.isclose(
        asteroid_2_attrs["diameter_m"], 600, rel_tol=1e-9
    )  # Largest diameter
    assert asteroid_2_attrs["hazardous"] == "No"
    assert asteroid_2_attrs["close_approach_date"] == "2024-Feb-01 00:00"
    assert asteroid_2_attrs["miss_distance_km"] == 500000
    assert asteroid_2_attrs["relative_velocity_kph"] == 15000


def test_extra_state_attributes_no_data() -> None:
    """Test extra_state_attributes behavior with no data."""
    mock_coordinator = MagicMock(data={DATA_SOURCE_NEOWS: []})

    # Use the first sensor description for testing
    description = SUMMARY_SENSOR_DESCRIPTIONS[0]
    sensor = NasaNeoSummarySensor(mock_coordinator, description)

    # Verify the attributes are empty
    assert sensor.extra_state_attributes == {}


# 4. Test  Handling of Missing or Malformed Data
def test_missing_data() -> None:
    """Test handling of missing data in the coordinator."""
    # Case 1: DATA_SOURCE_NEOWS key is not present
    mock_coordinator = MagicMock(data={})
    description = SUMMARY_SENSOR_DESCRIPTIONS[0]
    sensor = NasaNeoSummarySensor(mock_coordinator, description)

    assert sensor.native_value is None, "native_value should be None for missing data"
    assert (
        sensor.extra_state_attributes == {}
    ), "Attributes should be empty for missing data"

    # Case 2: DATA_SOURCE_NEOWS is None
    mock_coordinator = MagicMock(data={DATA_SOURCE_NEOWS: None})
    sensor = NasaNeoSummarySensor(mock_coordinator, description)

    assert sensor.native_value is None, "native_value should be None for None data"
    assert (
        sensor.extra_state_attributes == {}
    ), "Attributes should be empty for None data"


# 5. Test Unique ID and Device Information
