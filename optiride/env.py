"""Environmental physics calculations for air density."""

import math


def air_density_kg_m3(
    temperature_c: float,
    pressure_pa: float,
    humidity_frac: float = 0.0,
) -> float:
    """Calculate air density accounting for temperature, pressure, and humidity.

    Uses the Tetens equation for water vapor pressure and the ideal gas law
    for dry air and water vapor components.

    Args:
        temperature_c: Air temperature in degrees Celsius.
        pressure_pa: Atmospheric pressure in Pascals (typically ~101325 Pa at sea level).
        humidity_frac: Relative humidity as a fraction (0.0-1.0), defaults to 0.0.

    Returns:
        Air density in kg/m³.

    Example:
        >>> # Standard conditions: 15°C, 101325 Pa, 50% humidity
        >>> density = air_density_kg_m3(15.0, 101325.0, 0.5)
        >>> round(density, 3)
        1.225

    References:
        - Tetens equation: Bolton (1980), "The computation of equivalent potential
          temperature", Monthly Weather Review
        - Gas constants: ICAO Standard Atmosphere
    """
    temperature_k = temperature_c + 273.15

    # Water vapor saturation pressure using Tetens equation (Pa)
    p_ws = 610.94 * math.exp((17.625 * temperature_c) / (temperature_c + 243.04))

    # Actual water vapor pressure
    p_w = humidity_frac * p_ws

    # Dry air partial pressure
    p_d = pressure_pa - p_w

    # Specific gas constants (J/(kg·K))
    R_DRY_AIR = 287.058  # Dry air
    R_WATER_VAPOR = 461.495  # Water vapor

    # Air density from ideal gas law
    rho = p_d / (R_DRY_AIR * temperature_k) + p_w / (R_WATER_VAPOR * temperature_k)

    return rho
