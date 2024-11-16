"""Unit tests for the sensor components in the NASA API integration."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.components.nasa_api.const import DOMAIN
from homeassistant.components.nasa_api.sensor import (
    NasaNeoCountSensor,
    async_setup_entry,
)


@pytest.mark.asyncio
async def test_native_value() -> None:
    """Test that the sensor's native_value correctly reflects the NEO count."""

    # Mock the coordinator with sample data
    mock_coordinator = MagicMock()

    # Case 1: Coordinator data is empty
    mock_coordinator.data = []
    sensor = NasaNeoCountSensor(mock_coordinator)
    assert sensor.native_value == 0, "Sensor should return 0 when data is empty"

    # Case 2: Coordinator data has NEOs
    mock_coordinator.data = [{"id": 1}, {"id": 2}, {"id": 3}]
    sensor = NasaNeoCountSensor(mock_coordinator)
    assert sensor.native_value == 3, "Sensor should return the correct count of NEOs"

    # Case 3: Coordinator data is None
    mock_coordinator.data = None
    sensor = NasaNeoCountSensor(mock_coordinator)
    assert sensor.native_value == 0, "Sensor should return 0 when data is None"


# Testing coordinator integration


@pytest.mark.asyncio
async def test_coordinator_integration() -> None:
    """Test that the sensor updates correctly when the coordinator's data changes."""

    # Mock the coordinator
    mock_coordinator = MagicMock()
    mock_coordinator.data = []  # Initial state

    sensor = NasaNeoCountSensor(mock_coordinator)

    # Verify initial state
    assert sensor.native_value == 0, "Sensor should initialize with a count of 0"

    # Simulate an update from the coordinator
    mock_coordinator.data = [{"id": 1}, {"id": 2}, {"id": 3}]
    for listener in mock_coordinator.async_add_listener.call_args_list:
        listener[0][0]()  # Trigger the listeners manually

    # Verify the sensor reflects the updated coordinator data
    assert sensor.native_value == 3, "Sensor should update to reflect the new data"

    # Simulate another update from the coordinator
    mock_coordinator.data = [{"id": 1}]  # Reduced data
    for listener in mock_coordinator.async_add_listener.call_args_list:
        listener[0][0]()  # Trigger the listeners manually again

    # Verify the sensor reflects the updated data
    assert sensor.native_value == 1, "Sensor should update to reflect the reduced data"

    # Test empty data again
    mock_coordinator.data = []
    for listener in mock_coordinator.async_add_listener.call_args_list:
        listener[0][0]()  # Trigger the listeners manually one more time

    assert sensor.native_value == 0, "Sensor should return to 0 when data is empty"


# Testing unique ids
def test_unique_id() -> None:
    """Test that the unique_id is correctly set and unique."""

    # Mock the coordinator
    mock_coordinator = MagicMock()

    # Create the sensor
    sensor = NasaNeoCountSensor(mock_coordinator)

    # Verify that the unique_id is set correctly
    expected_unique_id = f"{DOMAIN}_neo_count"
    assert (
        sensor._attr_unique_id == expected_unique_id
    ), f"Expected unique_id to be {expected_unique_id}, but got {sensor._attr_unique_id}"

    # Verify the unique_id is indeed unique
    # In this case, since we only have one sensor entity, we just verify it is not None
    assert sensor._attr_unique_id is not None, "unique_id should not be None"


# Testing error handling


@pytest.mark.asyncio
async def test_error_handling() -> None:
    """Test the sensor's behavior when the coordinator provides invalid data."""

    # Mock the coordinator
    mock_coordinator = MagicMock()

    # Case 1: Coordinator data is None
    mock_coordinator.data = None
    sensor = NasaNeoCountSensor(mock_coordinator)
    try:
        assert (
            sensor.native_value == 0
        ), "Sensor should return 0 when coordinator data is None"
    except TypeError as e:
        pytest.fail(f"Sensor raised an exception with None data: {e}")

    # Case 2: Coordinator data is an empty list
    mock_coordinator.data = []
    sensor = NasaNeoCountSensor(mock_coordinator)
    try:
        assert (
            sensor.native_value == 0
        ), "Sensor should return 0 when coordinator data is empty"
    except TypeError as e:
        pytest.fail(f"Sensor raised an exception with empty data: {e}")

    # Case 3: Coordinator data is malformed (not a list)
    mock_coordinator.data = "invalid_string"
    sensor = NasaNeoCountSensor(mock_coordinator)
    try:
        assert (
            sensor.native_value == 0
        ), "Sensor should return 0 when data is not a list"
    except TypeError as e:
        pytest.fail(f"Sensor raised a TypeError with malformed data: {e}")


@pytest.mark.asyncio
async def test_async_setup_entry() -> None:
    """Test the async_setup_entry function."""

    # Mock the Home Assistant environment
    hass = MagicMock()
    async_add_entities = AsyncMock()

    # Mock the config entry and coordinator
    entry = MagicMock()
    entry.entry_id = "test_entry"
    mock_coordinator = MagicMock()
    hass.data = {DOMAIN: {entry.entry_id: mock_coordinator}}

    # Call the setup function
    await async_setup_entry(hass, entry, async_add_entities)

    # Verify that a sensor entity was added
    async_add_entities.assert_called_once()
    added_entities = async_add_entities.call_args[0][0]
    assert len(added_entities) == 1, "Only one entity should be added"
    assert isinstance(
        added_entities[0], NasaNeoCountSensor
    ), "The added entity should be a NasaNeoCountSensor"

    # Verify that the sensor is initialized with the correct coordinator
    assert (
        added_entities[0].coordinator == mock_coordinator
    ), "The sensor should be initialized with the correct coordinator"
