"""Tests for bike library database and configuration."""

import pytest

from optiride.bike_library import (
    BIKE_DATABASE,
    POSITION_DATABASE,
    WHEEL_DATABASE,
    BikeType,
    RidingPosition,
    WheelType,
    estimate_cda_from_height_mass,
    get_bike_config,
    get_simple_config,
    list_bike_types,
    list_positions,
    list_wheel_types,
)


class TestBikeDatabase:
    """Test bike database completeness and validity."""

    def test_all_bike_types_in_database(self) -> None:
        """Test that all BikeType enum values are in database."""
        for bike_type in BikeType:
            assert bike_type in BIKE_DATABASE

    def test_bike_specs_reasonable_values(self) -> None:
        """Test that all bike specs have reasonable physical values."""
        for spec in BIKE_DATABASE.values():
            # Mass should be between 5-15 kg for bikes
            assert 5.0 < spec.mass_kg < 15.0
            # CdA should be small and positive
            assert 0.0 < spec.base_cda < 0.2
            # Crr should be small
            assert 0.0 < spec.crr < 0.02
            # Efficiency should be between 0.9 and 1.0
            assert 0.9 < spec.drivetrain_efficiency <= 1.0

    def test_aero_bikes_have_lower_cda(self) -> None:
        """Test that aero bikes have better aerodynamics than standard bikes."""
        aero_cda = BIKE_DATABASE[BikeType.AERO_ROAD].base_cda
        endurance_cda = BIKE_DATABASE[BikeType.ROAD_ENDURANCE].base_cda
        assert aero_cda < endurance_cda

    def test_time_trial_bike_most_aero(self) -> None:
        """Test that TT bike has best aerodynamics."""
        tt_cda = BIKE_DATABASE[BikeType.TIME_TRIAL].base_cda
        for bike_type, spec in BIKE_DATABASE.items():
            if bike_type != BikeType.TIME_TRIAL:
                assert tt_cda <= spec.base_cda


class TestPositionDatabase:
    """Test riding position database."""

    def test_all_positions_in_database(self) -> None:
        """Test that all RidingPosition enum values are in database."""
        for position in RidingPosition:
            assert position in POSITION_DATABASE

    def test_position_cda_reasonable(self) -> None:
        """Test that position CdA values are reasonable."""
        for spec in POSITION_DATABASE.values():
            # Rider CdA should be between 0.15 and 0.40 m²
            assert 0.15 < spec.rider_cda < 0.40

    def test_aero_positions_better(self) -> None:
        """Test that aero positions have lower CdA than upright."""
        upright_cda = POSITION_DATABASE[RidingPosition.UPRIGHT].rider_cda
        drops_cda = POSITION_DATABASE[RidingPosition.DROPS].rider_cda
        tt_cda = POSITION_DATABASE[RidingPosition.TIME_TRIAL].rider_cda

        assert drops_cda < upright_cda
        assert tt_cda < drops_cda

    def test_super_tuck_most_aero(self) -> None:
        """Test that super tuck position is most aerodynamic."""
        super_tuck_cda = POSITION_DATABASE[RidingPosition.SUPER_TUCK].rider_cda
        for position, spec in POSITION_DATABASE.items():
            if position != RidingPosition.SUPER_TUCK:
                assert super_tuck_cda <= spec.rider_cda


class TestWheelDatabase:
    """Test wheel configuration database."""

    def test_all_wheel_types_in_database(self) -> None:
        """Test that all WheelType enum values are in database."""
        for wheel_type in WheelType:
            assert wheel_type in WHEEL_DATABASE

    def test_wheel_deltas_reasonable(self) -> None:
        """Test that wheel deltas are reasonable."""
        for spec in WHEEL_DATABASE.values():
            # Mass delta should be reasonable (±2 kg max)
            assert -2.0 < spec.mass_delta_kg < 2.0
            # CdA delta should be small
            assert -0.03 < spec.cda_delta < 0.03
            # Crr delta should be small
            assert -0.002 < spec.crr_delta < 0.002

    def test_shallow_alloy_is_baseline(self) -> None:
        """Test that shallow alloy wheels are the baseline (all deltas = 0)."""
        baseline = WHEEL_DATABASE[WheelType.SHALLOW_ALLOY]
        assert baseline.mass_delta_kg == 0.0
        assert baseline.cda_delta == 0.0
        assert baseline.crr_delta == 0.0

    def test_deep_wheels_more_aero(self) -> None:
        """Test that deep section wheels have better aero than shallow."""
        shallow_cda = WHEEL_DATABASE[WheelType.SHALLOW_ALLOY].cda_delta
        deep_cda = WHEEL_DATABASE[WheelType.DEEP_SECTION].cda_delta
        assert deep_cda < shallow_cda


class TestGetBikeConfig:
    """Test get_bike_config function."""

    def test_basic_config(self) -> None:
        """Test basic bike configuration retrieval."""
        config = get_bike_config(BikeType.AERO_ROAD, RidingPosition.DROPS)
        assert "mass_kg" in config
        assert "cda" in config
        assert "crr" in config
        assert "drivetrain_efficiency" in config

    def test_config_with_strings(self) -> None:
        """Test that string inputs work correctly."""
        config = get_bike_config("aero_road", "drops", "mid_depth")
        assert config["mass_kg"] > 0
        assert config["cda"] > 0

    def test_default_position_for_road_bike(self) -> None:
        """Test that road bikes default to drops position."""
        config = get_bike_config(BikeType.ROAD_RACE)
        # Should use drops position (CdA around 0.28 + 0.08 = 0.36)
        assert 0.30 < config["cda"] < 0.40

    def test_default_position_for_tt_bike(self) -> None:
        """Test that TT bikes default to TT position."""
        config = get_bike_config(BikeType.TIME_TRIAL)
        # Should use TT position (CdA around 0.22 + 0.06 = 0.28)
        assert 0.25 < config["cda"] < 0.35

    def test_wheel_effects(self) -> None:
        """Test that different wheels affect configuration."""
        config_shallow = get_bike_config("aero_road", "drops", "shallow_alloy")
        config_deep = get_bike_config("aero_road", "drops", "deep_section")

        # Deep wheels should have lower CdA
        assert config_deep["cda"] < config_shallow["cda"]

    def test_invalid_bike_type_raises_error(self) -> None:
        """Test that invalid bike type raises KeyError."""
        with pytest.raises(ValueError):
            get_bike_config("invalid_bike")

    def test_config_values_reasonable(self) -> None:
        """Test that returned config values are physically reasonable."""
        config = get_bike_config("road_race", "drops", "mid_depth")

        # Total mass should be reasonable (7-10 kg for race bike)
        assert 7.0 < config["mass_kg"] < 10.0
        # Total CdA should be reasonable (0.3-0.4 m² typical)
        assert 0.25 < config["cda"] < 0.45
        # Crr should be small
        assert 0.002 < config["crr"] < 0.01
        # Efficiency high
        assert 0.95 < config["drivetrain_efficiency"] <= 1.0

    def test_cda_adjusted_for_rider_size(self) -> None:
        """Test that CdA is adjusted based on rider height and mass."""
        # Reference rider (1.80m, 75kg)
        config_ref = get_bike_config("aero_road", "drops", rider_height_m=1.80, rider_mass_kg=75.0)

        # Smaller rider (1.65m, 60kg) should have lower CdA
        config_small = get_bike_config(
            "aero_road", "drops", rider_height_m=1.65, rider_mass_kg=60.0
        )
        assert config_small["cda"] < config_ref["cda"]

        # Larger rider (1.95m, 90kg) should have higher CdA
        config_large = get_bike_config(
            "aero_road", "drops", rider_height_m=1.95, rider_mass_kg=90.0
        )
        assert config_large["cda"] > config_ref["cda"]

    def test_cda_with_only_height(self) -> None:
        """Test that CdA adjustment works with only height provided."""
        config_short = get_bike_config("aero_road", "drops", rider_height_m=1.65)
        config_tall = get_bike_config("aero_road", "drops", rider_height_m=1.95)

        # Taller rider should have higher CdA
        assert config_tall["cda"] > config_short["cda"]

    def test_cda_with_only_mass(self) -> None:
        """Test that CdA adjustment works with only mass provided."""
        config_light = get_bike_config("aero_road", "drops", rider_mass_kg=60.0)
        config_heavy = get_bike_config("aero_road", "drops", rider_mass_kg=90.0)

        # Heavier rider should have higher CdA
        assert config_heavy["cda"] > config_light["cda"]

    def test_cda_without_rider_info_uses_defaults(self) -> None:
        """Test that without rider info, reference values are used."""
        config_no_rider = get_bike_config("aero_road", "drops")
        config_ref_rider = get_bike_config(
            "aero_road", "drops", rider_height_m=1.80, rider_mass_kg=75.0
        )

        # Should be identical (both use reference rider)
        assert abs(config_no_rider["cda"] - config_ref_rider["cda"]) < 0.001


class TestGetSimpleConfig:
    """Test get_simple_config convenience function."""

    def test_simple_config_with_defaults(self) -> None:
        """Test simple config with default parameters."""
        config = get_simple_config()
        assert config["mass_kg"] > 0
        assert config["cda"] > 0

    def test_simple_config_custom_bike(self) -> None:
        """Test simple config with custom bike type."""
        config = get_simple_config(bike_type="time_trial")
        # TT bike should have lower CdA
        assert config["cda"] < 0.35


class TestEstimateCdaFromHeightMass:
    """Test CdA estimation from anthropometric data."""

    def test_reference_rider(self) -> None:
        """Test that reference rider (1.80m, 75kg) gives expected CdA."""
        cda = estimate_cda_from_height_mass(1.80, 75.0, RidingPosition.DROPS)
        expected = POSITION_DATABASE[RidingPosition.DROPS].rider_cda
        # Should be very close to reference value
        assert abs(cda - expected) < 0.001

    def test_taller_rider_higher_cda(self) -> None:
        """Test that taller riders have higher CdA."""
        cda_short = estimate_cda_from_height_mass(1.60, 75.0, "drops")
        cda_tall = estimate_cda_from_height_mass(2.00, 75.0, "drops")
        assert cda_tall > cda_short

    def test_heavier_rider_higher_cda(self) -> None:
        """Test that heavier riders have higher CdA."""
        cda_light = estimate_cda_from_height_mass(1.80, 60.0, "drops")
        cda_heavy = estimate_cda_from_height_mass(1.80, 90.0, "drops")
        assert cda_heavy > cda_light

    def test_cda_values_reasonable(self) -> None:
        """Test that estimated CdA values are reasonable."""
        # Small rider
        cda_small = estimate_cda_from_height_mass(1.60, 55.0, "drops")
        assert 0.20 < cda_small < 0.35

        # Large rider
        cda_large = estimate_cda_from_height_mass(2.00, 100.0, "drops")
        assert 0.30 < cda_large < 0.50

    def test_different_positions(self) -> None:
        """Test CdA estimation works for different positions."""
        cda_upright = estimate_cda_from_height_mass(1.80, 75.0, "upright")
        cda_tt = estimate_cda_from_height_mass(1.80, 75.0, "time_trial")
        assert cda_upright > cda_tt


class TestListFunctions:
    """Test list functions for available options."""

    def test_list_bike_types(self) -> None:
        """Test that list_bike_types returns all bike types."""
        bike_types = list_bike_types()
        assert len(bike_types) > 0
        assert "aero_road" in bike_types
        assert "time_trial" in bike_types

    def test_list_positions(self) -> None:
        """Test that list_positions returns all positions."""
        positions = list_positions()
        assert len(positions) > 0
        assert "drops" in positions
        assert "time_trial" in positions

    def test_list_wheel_types(self) -> None:
        """Test that list_wheel_types returns all wheel types."""
        wheel_types = list_wheel_types()
        assert len(wheel_types) > 0
        assert "mid_depth" in wheel_types
        assert "disc_rear" in wheel_types
