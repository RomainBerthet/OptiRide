"""Tests for physics calculations."""

from optiride.models import Environment, RiderBike
from optiride.physics import (
    GRAVITY,
    power_required,
    relative_air_speed,
    speed_from_power,
)


class TestRelativeAirSpeed:
    """Test relative air speed calculations."""

    def test_no_wind(self, standard_environment: Environment) -> None:
        """Test that with no wind, relative speed equals rider speed."""
        v_rel = relative_air_speed(10.0, 0.0, standard_environment)
        assert abs(v_rel - 10.0) < 0.001

    def test_headwind(self) -> None:
        """Test relative speed with headwind (riding north into north wind)."""
        env = Environment(air_density=1.225, wind_u_ms=0.0, wind_v_ms=5.0)
        v_rel = relative_air_speed(10.0, 0.0, env)  # Riding north

        # Headwind increases relative air speed
        assert v_rel > 10.0
        assert abs(v_rel - 15.0) < 0.001

    def test_tailwind(self) -> None:
        """Test relative speed with tailwind (riding north with south wind)."""
        env = Environment(air_density=1.225, wind_u_ms=0.0, wind_v_ms=-5.0)
        v_rel = relative_air_speed(10.0, 0.0, env)  # Riding north

        # Tailwind decreases relative air speed
        assert v_rel < 10.0
        assert abs(v_rel - 5.0) < 0.001


class TestPowerRequired:
    """Test power requirement calculations."""

    def test_flat_terrain_no_wind(
        self, standard_rider: RiderBike, standard_environment: Environment
    ) -> None:
        """Test power on flat terrain with no wind."""
        power = power_required(10.0, 0.0, 0.0, standard_rider, standard_environment)

        # Should be positive and in reasonable range
        assert power > 0
        assert 100 < power < 300

    def test_climbing(self, standard_rider: RiderBike, standard_environment: Environment) -> None:
        """Test that climbing requires more power than flat."""
        power_flat = power_required(10.0, 0.0, 0.0, standard_rider, standard_environment)
        power_climb = power_required(
            10.0, 0.05, 0.0, standard_rider, standard_environment
        )  # 5% grade

        assert power_climb > power_flat

    def test_descending(self, standard_rider: RiderBike, standard_environment: Environment) -> None:
        """Test power on descent."""
        power_flat = power_required(10.0, 0.0, 0.0, standard_rider, standard_environment)
        power_down = power_required(
            10.0, -0.05, 0.0, standard_rider, standard_environment
        )  # -5% grade

        # Descending requires less power
        assert power_down < power_flat

    def test_faster_speed_more_power(
        self, standard_rider: RiderBike, standard_environment: Environment
    ) -> None:
        """Test that higher speed requires more power (primarily due to aero drag)."""
        power_slow = power_required(8.0, 0.0, 0.0, standard_rider, standard_environment)
        power_fast = power_required(12.0, 0.0, 0.0, standard_rider, standard_environment)

        assert power_fast > power_slow

    def test_non_negative_power(
        self, standard_rider: RiderBike, standard_environment: Environment
    ) -> None:
        """Test that power is always non-negative."""
        # Even on steep descent
        power = power_required(15.0, -0.10, 0.0, standard_rider, standard_environment)  # -10% grade

        assert power >= 0.0


class TestSpeedFromPower:
    """Test speed calculation from power."""

    def test_reasonable_speed_range(
        self, standard_rider: RiderBike, standard_environment: Environment
    ) -> None:
        """Test that calculated speed is in reasonable range."""
        speed = speed_from_power(200.0, 0.0, 0.0, standard_rider, standard_environment)

        # 200W on flat should give ~30-40 km/h (8-11 m/s)
        assert 8.0 < speed < 12.0

    def test_more_power_more_speed(
        self, standard_rider: RiderBike, standard_environment: Environment
    ) -> None:
        """Test that more power yields higher speed."""
        speed_low = speed_from_power(150.0, 0.0, 0.0, standard_rider, standard_environment)
        speed_high = speed_from_power(250.0, 0.0, 0.0, standard_rider, standard_environment)

        assert speed_high > speed_low

    def test_climbing_slower(
        self, standard_rider: RiderBike, standard_environment: Environment
    ) -> None:
        """Test that same power yields lower speed when climbing."""
        speed_flat = speed_from_power(200.0, 0.0, 0.0, standard_rider, standard_environment)
        speed_climb = speed_from_power(
            200.0, 0.05, 0.0, standard_rider, standard_environment
        )  # 5% grade

        assert speed_climb < speed_flat

    def test_inverse_of_power_required(
        self, standard_rider: RiderBike, standard_environment: Environment
    ) -> None:
        """Test that speed_from_power is inverse of power_required."""
        target_speed = 10.0
        power = power_required(target_speed, 0.02, 0.0, standard_rider, standard_environment)
        calculated_speed = speed_from_power(power, 0.02, 0.0, standard_rider, standard_environment)

        # Should recover original speed (within numerical tolerance)
        assert abs(calculated_speed - target_speed) < 0.01


class TestConstants:
    """Test physical constants."""

    def test_gravity_constant(self) -> None:
        """Test that gravity constant is correct."""
        assert abs(GRAVITY - 9.80665) < 0.00001
