"""Model definitions for the NASA API objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import LOGGER


@dataclass(slots=True)
class NeoWsAsteroid:
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
    def from_dict(cls, data: dict[str, Any]) -> NeoWsAsteroid:
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


@dataclass(slots=True)
class ApodImage:
    """Represents Astronomy Picture of the Day (APOD) data."""

    date: str
    explanation: str
    hdurl: str
    media_type: str
    title: str
    url: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApodImage:
        """Initialize from a dictionary."""
        try:
            return cls(
                date=data["date"],
                explanation=data["explanation"],
                hdurl=data.get("hdurl", ""),
                media_type=data["media_type"],
                title=data["title"],
                url=data["url"],
            )
        except KeyError as err:
            raise ValueError(f"Missing required field in APOD data: {err}") from err


@dataclass(slots=True)
class MarsWeather:
    """Represents Mars weather data for a single Sol (Martian day)."""

    sol: str  # Sol number (Martian day)
    temperature: float | None  # Average atmospheric temperature
    temperature_min: float | None  # Minimum temperature
    temperature_max: float | None  # Maximum temperature
    pressure: float | None  # Average atmospheric pressure
    wind_speed: float | None  # Average wind speed
    wind_bearing: float | None  # Most common wind direction in degrees
    season: str | None  # Martian season
    first_utc: str | None  # Start UTC timestamp for this Sol
    last_utc: str | None  # End UTC timestamp for this Sol

    @classmethod
    def from_dict(cls, sol: str, data: dict[str, Any]) -> MarsWeather:
        """Initialize MarsWeather from a dictionary."""
        return cls(
            sol=sol,
            temperature=data.get("AT", {}).get("av"),
            temperature_min=data.get("AT", {}).get("mn"),
            temperature_max=data.get("AT", {}).get("mx"),
            pressure=data.get("PRE", {}).get("av"),
            wind_speed=data.get("HWS", {}).get("av"),
            wind_bearing=data.get("WD", {})
            .get("most_common", {})
            .get("compass_degrees"),
            season=data.get("Season"),
            first_utc=data.get("First_UTC"),
            last_utc=data.get("Last_UTC"),
        )


def parse_mars_weather(data: dict[str, Any]) -> list[MarsWeather]:
    """Parse raw Mars weather API data into a list of MarsWeather objects."""
    sol_keys = data.get("sol_keys", [])
    weather_data: list[MarsWeather] = []

    if not sol_keys:
        LOGGER.warning("No Sol keys found in API data")
        return weather_data

    for sol in sol_keys:
        sol_data = data.get(sol, {})
        if not sol_data:
            LOGGER.warning(f"No data found for Sol {sol}")
            continue

        weather_data.append(MarsWeather.from_dict(sol, sol_data))

    return weather_data
