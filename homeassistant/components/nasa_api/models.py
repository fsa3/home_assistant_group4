"""Model definitions for the NASA API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Neo:
    """Represents a near-Earth object (asteroid)."""

    id: str
    name: str
    nasa_jpl_url: str
    absolute_magnitude_h: float
    estimated_diameter: EstimatedDiameter
    is_potentially_hazardous: bool
    close_approach_data: list[CloseApproachData]
    is_sentry_object: bool
    sentry_data_url: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Neo:
        """Initialize from a dictionary."""
        close_approach_data = [
            CloseApproachData.from_dict(approach)
            for approach in data.get("close_approach_data", [])
        ]

        return cls(
            id=data["id"],
            name=data["name"],
            nasa_jpl_url=data["nasa_jpl_url"],
            absolute_magnitude_h=data["absolute_magnitude_h"],
            estimated_diameter=EstimatedDiameter.from_dict(data["estimated_diameter"]),
            is_potentially_hazardous=data["is_potentially_hazardous_asteroid"],
            close_approach_data=close_approach_data,
            is_sentry_object=data["is_sentry_object"],
            sentry_data_url=data.get("sentry_data"),
        )


@dataclass(slots=True)
class EstimatedDiameter:
    """Represents the estimated diameter of the asteroid."""

    min_km: float
    max_km: float
    min_meters: float
    max_meters: float
    min_miles: float
    max_miles: float
    min_feet: float
    max_feet: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EstimatedDiameter:
        """Initialize from a dictionary."""
        return cls(
            min_km=data["kilometers"]["estimated_diameter_min"],
            max_km=data["kilometers"]["estimated_diameter_max"],
            min_meters=data["meters"]["estimated_diameter_min"],
            max_meters=data["meters"]["estimated_diameter_max"],
            min_miles=data["miles"]["estimated_diameter_min"],
            max_miles=data["miles"]["estimated_diameter_max"],
            min_feet=data["feet"]["estimated_diameter_min"],
            max_feet=data["feet"]["estimated_diameter_max"],
        )


@dataclass(slots=True)
class CloseApproachData:
    """Represents close approach data for the asteroid."""

    close_approach_date: str
    close_approach_date_full: str
    epoch_date_close_approach: int
    relative_velocity_kps: float
    relative_velocity_kph: float
    relative_velocity_mph: float
    miss_distance_au: float
    miss_distance_lunar: float
    miss_distance_km: float
    miss_distance_miles: float
    orbiting_body: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CloseApproachData:
        """Initialize from a dictionary."""
        return cls(
            close_approach_date=data["close_approach_date"],
            close_approach_date_full=data["close_approach_date_full"],
            epoch_date_close_approach=data["epoch_date_close_approach"],
            relative_velocity_kps=float(
                data["relative_velocity"]["kilometers_per_second"]
            ),
            relative_velocity_kph=float(
                data["relative_velocity"]["kilometers_per_hour"]
            ),
            relative_velocity_mph=float(data["relative_velocity"]["miles_per_hour"]),
            miss_distance_au=float(data["miss_distance"]["astronomical"]),
            miss_distance_lunar=float(data["miss_distance"]["lunar"]),
            miss_distance_km=float(data["miss_distance"]["kilometers"]),
            miss_distance_miles=float(data["miss_distance"]["miles"]),
            orbiting_body=data["orbiting_body"],
        )
