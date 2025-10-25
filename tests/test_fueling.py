"""Tests for the fueling module."""

import numpy as np
import pytest

from optiride.fueling import (
    FuelingPoint,
    calculate_fatigue_index,
    calculate_fueling_points,
    calculate_power_zones,
    calculate_w_prime_balance,
    get_power_zone_name,
)


class TestPowerZones:
    """Test power zone calculations."""

    def test_power_zones_based_on_ftp(self) -> None:
        """Test that power zones are correctly calculated based on FTP."""
        ftp = 260.0
        zones = calculate_power_zones(ftp)

        assert zones["recovery"] == (0.0, 143.0)
        assert zones["endurance"] == (143.0, 195.0)
        assert zones["tempo"] == (195.0, 234.0)
        assert zones["threshold"] == (234.0, 273.0)
        assert zones["vo2max"] == (273.0, 312.0)
        assert zones["anaerobic"] == (312.0, float("inf"))

    def test_power_zones_scale_with_ftp(self) -> None:
        """Test that power zones scale proportionally with FTP."""
        ftp1 = 200.0
        ftp2 = 300.0
        zones1 = calculate_power_zones(ftp1)
        zones2 = calculate_power_zones(ftp2)

        # Check that zones scale by the same ratio as FTP
        ratio = ftp2 / ftp1
        assert zones2["tempo"][0] / zones1["tempo"][0] == pytest.approx(ratio, abs=0.01)
        assert zones2["threshold"][1] / zones1["threshold"][1] == pytest.approx(ratio, abs=0.01)

    def test_get_power_zone_name(self) -> None:
        """Test power zone name lookup."""
        ftp = 260.0

        assert get_power_zone_name(100, ftp) == "recovery"
        assert get_power_zone_name(170, ftp) == "endurance"
        assert get_power_zone_name(210, ftp) == "tempo"
        assert get_power_zone_name(250, ftp) == "threshold"
        assert get_power_zone_name(290, ftp) == "vo2max"
        assert get_power_zone_name(350, ftp) == "anaerobic"


class TestWPrimeBalance:
    """Test W' balance calculations."""

    def test_starts_at_full_capacity(self) -> None:
        """Test that W' balance starts at 100%."""
        powers = np.array([200.0, 200.0, 200.0])
        times = np.array([0.0, 60.0, 120.0])
        cp = 250.0
        w_prime = 20000.0

        w_balance = calculate_w_prime_balance(powers, times, cp, w_prime)

        assert w_balance[0] == pytest.approx(1.0)

    def test_depletes_above_cp(self) -> None:
        """Test that W' depletes when riding above CP."""
        powers = np.array([300.0, 300.0, 300.0, 300.0])
        times = np.array([0.0, 60.0, 120.0, 180.0])
        cp = 250.0
        w_prime = 20000.0

        w_balance = calculate_w_prime_balance(powers, times, cp, w_prime)

        # Should deplete over time when above CP
        assert w_balance[1] < w_balance[0]
        assert w_balance[2] < w_balance[1]
        assert w_balance[3] < w_balance[2]

    def test_recovers_below_cp(self) -> None:
        """Test that W' recovers when riding below CP."""
        # First deplete, then recover
        powers = np.array([300.0, 300.0, 200.0, 200.0])
        times = np.array([0.0, 60.0, 120.0, 240.0])
        cp = 250.0
        w_prime = 20000.0

        w_balance = calculate_w_prime_balance(powers, times, cp, w_prime)

        # Should recover after dropping below CP
        assert w_balance[2] < w_balance[1]  # Still depleting at transition
        assert w_balance[3] > w_balance[2]  # Recovering

    def test_clamped_to_valid_range(self) -> None:
        """Test that W' balance is clamped between 0 and 1."""
        powers = np.array([500.0] * 100)  # Very high power
        times = np.arange(0, 100 * 60, 60, dtype=float)
        cp = 250.0
        w_prime = 20000.0

        w_balance = calculate_w_prime_balance(powers, times, cp, w_prime)

        assert np.all(w_balance >= 0.0)
        assert np.all(w_balance <= 1.0)

    def test_no_cp_returns_full_capacity(self) -> None:
        """Test that when CP/W' not available, returns 100%."""
        powers = np.array([200.0, 300.0, 250.0])
        times = np.array([0.0, 60.0, 120.0])

        w_balance = calculate_w_prime_balance(powers, times, None, None)  # type: ignore

        assert np.all(w_balance == 1.0)


class TestFatigueIndex:
    """Test fatigue index calculations."""

    def test_fresh_rider_low_fatigue(self) -> None:
        """Test that fresh rider with full W' has low fatigue."""
        fatigue = calculate_fatigue_index(w_prime_balance_pct=1.0, time_h=0.5, intensity_factor=0.7)
        assert fatigue < 30.0

    def test_depleted_w_prime_increases_fatigue(self) -> None:
        """Test that depleted W' increases fatigue."""
        fatigue_high = calculate_fatigue_index(
            w_prime_balance_pct=0.2, time_h=1.0, intensity_factor=0.75
        )
        fatigue_low = calculate_fatigue_index(
            w_prime_balance_pct=0.8, time_h=1.0, intensity_factor=0.75
        )
        assert fatigue_high > fatigue_low

    def test_long_duration_increases_fatigue(self) -> None:
        """Test that longer duration increases fatigue."""
        fatigue_short = calculate_fatigue_index(
            w_prime_balance_pct=0.7, time_h=1.0, intensity_factor=0.75
        )
        fatigue_long = calculate_fatigue_index(
            w_prime_balance_pct=0.7, time_h=5.0, intensity_factor=0.75
        )
        assert fatigue_long > fatigue_short

    def test_high_intensity_increases_fatigue(self) -> None:
        """Test that higher intensity increases fatigue."""
        fatigue_easy = calculate_fatigue_index(
            w_prime_balance_pct=0.7, time_h=2.0, intensity_factor=0.65
        )
        fatigue_hard = calculate_fatigue_index(
            w_prime_balance_pct=0.7, time_h=2.0, intensity_factor=0.95
        )
        assert fatigue_hard > fatigue_easy

    def test_fatigue_clamped_to_100(self) -> None:
        """Test that fatigue is clamped to maximum 100."""
        fatigue = calculate_fatigue_index(
            w_prime_balance_pct=0.0, time_h=10.0, intensity_factor=1.1
        )
        assert fatigue <= 100.0


class TestCalculateFuelingPoints:
    """Test fueling point calculation."""

    def test_short_ride_no_refueling(self) -> None:
        """Test that short rides (<30min) don't generate refueling points."""
        distances = np.array([0.0, 5.0, 10.0])
        times = np.array([0.0, 0.15, 0.3])  # 18 minutes
        powers = np.array([200.0, 220.0, 210.0])

        points = calculate_fueling_points(distances, times, powers, ftp=260.0)

        assert len(points) == 0

    def test_long_ride_generates_refueling_points(self) -> None:
        """Test that long rides generate appropriate refueling points."""
        # 3 hour ride
        n_points = 180
        distances = np.linspace(0, 100, n_points)
        times = np.linspace(0, 3.0, n_points)
        powers = np.full(n_points, 220.0)

        points = calculate_fueling_points(
            distances, times, powers, ftp=260.0, refuel_interval_min=20.0
        )

        # Should have ~9 refueling points (3h * 60min/h / 20min)
        assert len(points) >= 8
        assert len(points) <= 10

    def test_fueling_point_has_all_attributes(self) -> None:
        """Test that fueling points have all required attributes."""
        distances = np.linspace(0, 80, 120)
        times = np.linspace(0, 2.5, 120)
        powers = np.full(120, 240.0)

        points = calculate_fueling_points(distances, times, powers, ftp=260.0)

        assert len(points) > 0
        point = points[0]

        assert isinstance(point, FuelingPoint)
        assert point.distance_km > 0
        assert point.time_h > 0
        assert point.carbs_g > 0
        assert point.fluids_ml > 0
        assert point.sodium_mg > 0
        assert 0 <= point.w_prime_balance_pct <= 1
        assert 0 <= point.fatigue_index <= 100
        assert point.refuel_type in ["gel", "bar", "drink", "solid"]
        assert len(point.notes) > 0

    def test_high_fatigue_recommends_gels(self) -> None:
        """Test that high fatigue leads to gel recommendations."""
        # Create scenario with depleting W' (high intensity)
        n_points = 120
        distances = np.linspace(0, 60, n_points)
        times = np.linspace(0, 2.0, n_points)
        powers = np.full(n_points, 280.0)  # High intensity (>FTP)

        points = calculate_fueling_points(
            distances,
            times,
            powers,
            ftp=260.0,
            cp=260.0,
            w_prime=20000.0,
            refuel_interval_min=20.0,
        )

        # Later refueling points should favor gels due to fatigue
        if len(points) > 2:
            assert any(p.refuel_type == "gel" for p in points[-2:])

    def test_carbs_scale_with_interval(self) -> None:
        """Test that carb amounts scale with refueling interval."""
        distances = np.linspace(0, 80, 120)
        times = np.linspace(0, 2.5, 120)
        powers = np.full(120, 220.0)

        points_20min = calculate_fueling_points(
            distances, times, powers, ftp=260.0, refuel_interval_min=20.0, carbs_per_hour=60.0
        )

        points_30min = calculate_fueling_points(
            distances, times, powers, ftp=260.0, refuel_interval_min=30.0, carbs_per_hour=60.0
        )

        # 30min interval should have ~1.5x more carbs per point
        if points_20min and points_30min:
            ratio = points_30min[0].carbs_g / points_20min[0].carbs_g
            assert ratio == pytest.approx(1.5, abs=0.2)

    def test_without_cp_w_prime_still_works(self) -> None:
        """Test that fueling calculation works without CP/W' data."""
        distances = np.linspace(0, 60, 90)
        times = np.linspace(0, 2.0, 90)
        powers = np.full(90, 220.0)

        points = calculate_fueling_points(
            distances, times, powers, ftp=260.0, cp=None, w_prime=None
        )

        assert len(points) > 0
        # W' balance should be 100% throughout
        assert all(p.w_prime_balance_pct == 1.0 for p in points)

    def test_energy_deficit_increases_over_time(self) -> None:
        """Test that energy deficit accumulates over the ride."""
        distances = np.linspace(0, 80, 120)
        times = np.linspace(0, 2.5, 120)
        powers = np.full(120, 240.0)

        points = calculate_fueling_points(distances, times, powers, ftp=260.0)

        # Energy deficit should increase at each refueling point
        for i in range(1, len(points)):
            assert points[i].energy_deficit_kcal > points[i - 1].energy_deficit_kcal
