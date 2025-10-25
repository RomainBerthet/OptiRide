"""Tests for data models."""

from optiride.models import Environment, RiderBike


class TestRiderBike:
    """Test RiderBike model."""

    def test_initialization(self) -> None:
        """Test RiderBike initialization with required parameters."""
        rider = RiderBike(
            mass_rider_kg=72.0,
            mass_bike_kg=8.0,
            crr=0.0035,
            cda=0.30,
        )

        assert rider.mass_rider_kg == 72.0
        assert rider.mass_bike_kg == 8.0
        assert rider.crr == 0.0035
        assert rider.cda == 0.30
        assert rider.drivetrain_eff == 0.97  # Default value

    def test_total_mass(self) -> None:
        """Test mass_system_kg property."""
        rider = RiderBike(
            mass_rider_kg=72.0,
            mass_bike_kg=8.0,
            crr=0.0035,
            cda=0.30,
        )

        assert rider.mass_system_kg == 80.0

    def test_with_power_parameters(self) -> None:
        """Test RiderBike with FTP and W' parameters."""
        rider = RiderBike(
            mass_rider_kg=72.0,
            mass_bike_kg=8.0,
            crr=0.0035,
            cda=0.30,
            ftp=260.0,
            w_prime_j=20000.0,
        )

        assert rider.ftp == 260.0
        assert rider.w_prime_j == 20000.0
        assert rider.cp is None  # Not set


class TestEnvironment:
    """Test Environment model."""

    def test_initialization_no_wind(self) -> None:
        """Test Environment initialization without wind."""
        env = Environment(air_density=1.225)

        assert env.air_density == 1.225
        assert env.wind_u_ms == 0.0
        assert env.wind_v_ms == 0.0

    def test_initialization_with_wind(self) -> None:
        """Test Environment initialization with wind components."""
        env = Environment(
            air_density=1.225,
            wind_u_ms=3.0,
            wind_v_ms=-2.0,
        )

        assert env.air_density == 1.225
        assert env.wind_u_ms == 3.0
        assert env.wind_v_ms == -2.0
