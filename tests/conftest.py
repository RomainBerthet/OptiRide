"""Pytest configuration and fixtures."""

import pytest

from optiride.models import Environment, RiderBike


@pytest.fixture
def standard_rider() -> RiderBike:
    """Create a standard rider/bike configuration for testing."""
    return RiderBike(
        mass_rider_kg=72.0,
        mass_bike_kg=8.0,
        crr=0.0035,
        cda=0.30,
        drivetrain_eff=0.97,
        ftp=260.0,
        w_prime_j=20000.0,
    )


@pytest.fixture
def standard_environment() -> Environment:
    """Create standard atmospheric conditions for testing."""
    return Environment(
        air_density=1.225,  # Standard sea level density
        wind_u_ms=0.0,
        wind_v_ms=0.0,
    )


@pytest.fixture
def windy_environment() -> Environment:
    """Create windy conditions for testing."""
    return Environment(
        air_density=1.225,
        wind_u_ms=3.0,  # 3 m/s eastward wind
        wind_v_ms=-2.0,  # 2 m/s southward wind
    )
