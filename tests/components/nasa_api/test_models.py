"""Unit tests for the models used in the NASA API integration."""

import math
import unittest

import pytest

from homeassistant.components.nasa_api.models import NeoWsAsteroid


class TestNeoWsAsteroid(unittest.TestCase):
    """Unit tests for the NeoWsAsteroid model."""

    def test_from_dict_successful_initialization(self):
        """Test NeoWsAsteroid initializes correctly from a valid dictionary."""
        data = {
            "id": "12345",
            "name": "TestAsteroid",
            "nasa_jpl_url": "https://example.com",
            "absolute_magnitude_h": 22.5,
            "estimated_diameter": {
                "kilometers": {
                    "estimated_diameter_min": 0.1,
                    "estimated_diameter_max": 0.5,
                },
                "meters": {
                    "estimated_diameter_min": 100,
                    "estimated_diameter_max": 500,
                },
                "miles": {
                    "estimated_diameter_min": 0.06,
                    "estimated_diameter_max": 0.31,
                },
                "feet": {"estimated_diameter_min": 328, "estimated_diameter_max": 1640},
            },
            "is_potentially_hazardous_asteroid": True,
            "close_approach_data": [
                {
                    "close_approach_date": "2024-11-13",
                    "close_approach_date_full": "2024-Nov-13 00:00",
                    "epoch_date_close_approach": 1700000000,
                    "relative_velocity": {
                        "kilometers_per_second": "10.0",
                        "kilometers_per_hour": "36000",
                        "miles_per_hour": "22369.4",
                    },
                    "miss_distance": {
                        "astronomical": "0.05",
                        "lunar": "19.5",
                        "kilometers": "7500000",
                        "miles": "4660000",
                    },
                    "orbiting_body": "Earth",
                }
            ],
            "is_sentry_object": False,
            "sentry_data": None,
        }

        asteroid = NeoWsAsteroid.from_dict(data)

        # Verify core attributes
        assert asteroid.id == "12345"
        assert asteroid.name == "TestAsteroid"
        assert asteroid.is_potentially_hazardous is True

        # Verify estimated diameter
        assert math.isclose(asteroid.estimated_diameter.min_km, 0.1, rel_tol=1e-9)
        assert math.isclose(asteroid.estimated_diameter.max_km, 0.5, rel_tol=1e-9)

        # Verify close approach data
        assert len(asteroid.close_approach_data) == 1
        close_approach = asteroid.close_approach_data[0]
        assert close_approach.close_approach_date == "2024-11-13"
        assert math.isclose(close_approach.relative_velocity_kps, 10.0, rel_tol=1e-9)

    def test_missing_fields(self):
        """Test NeoWsAsteroid initialization with missing fields raises KeyError or similar."""
        incomplete_data = {
            "id": "12345",
            # intentionally missing 'name' and other fields
            "absolute_magnitude_h": 22.5,
        }

        with pytest.raises(KeyError):
            NeoWsAsteroid.from_dict(incomplete_data)


# Run tests
if __name__ == "__main__":
    unittest.main()
