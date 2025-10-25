"""Tests for environmental calculations."""

from optiride.env import air_density_kg_m3


class TestAirDensity:
    """Test air density calculations."""

    def test_standard_conditions(self) -> None:
        """Test air density at standard conditions (15°C, 101325 Pa, dry air)."""
        rho = air_density_kg_m3(15.0, 101325.0, 0.0)

        # Standard air density is approximately 1.225 kg/m³
        assert 1.22 < rho < 1.23

    def test_hot_conditions(self) -> None:
        """Test that hot air is less dense."""
        rho_standard = air_density_kg_m3(15.0, 101325.0, 0.0)
        rho_hot = air_density_kg_m3(35.0, 101325.0, 0.0)

        assert rho_hot < rho_standard

    def test_cold_conditions(self) -> None:
        """Test that cold air is more dense."""
        rho_standard = air_density_kg_m3(15.0, 101325.0, 0.0)
        rho_cold = air_density_kg_m3(-10.0, 101325.0, 0.0)

        assert rho_cold > rho_standard

    def test_high_pressure(self) -> None:
        """Test that high pressure increases density."""
        rho_standard = air_density_kg_m3(15.0, 101325.0, 0.0)
        rho_high_pressure = air_density_kg_m3(15.0, 105000.0, 0.0)

        assert rho_high_pressure > rho_standard

    def test_low_pressure(self) -> None:
        """Test that low pressure (altitude) decreases density."""
        rho_standard = air_density_kg_m3(15.0, 101325.0, 0.0)
        rho_altitude = air_density_kg_m3(15.0, 85000.0, 0.0)  # ~1500m altitude

        assert rho_altitude < rho_standard

    def test_humidity_effect(self) -> None:
        """Test that humidity slightly decreases density."""
        rho_dry = air_density_kg_m3(25.0, 101325.0, 0.0)
        rho_humid = air_density_kg_m3(25.0, 101325.0, 0.8)  # 80% humidity

        # Humid air is slightly less dense (water vapor is lighter than dry air)
        assert rho_humid < rho_dry

    def test_realistic_range(self) -> None:
        """Test density is in realistic range for various conditions."""
        # Sea level, hot summer day
        rho_hot = air_density_kg_m3(35.0, 101325.0, 0.6)
        assert 1.10 < rho_hot < 1.18

        # Sea level, cold winter day
        rho_cold = air_density_kg_m3(-10.0, 102000.0, 0.2)
        assert 1.30 < rho_cold < 1.38

        # High altitude (~2000m), moderate temperature
        rho_altitude = air_density_kg_m3(15.0, 80000.0, 0.3)
        assert 0.95 < rho_altitude < 1.05
