"""Cycling physics calculations based on Martin et al. (1998)."""

import math

from optiride.models import Environment, RiderBike

# Standard gravity (m/s²) - CODATA 2018 recommended value
GRAVITY = 9.80665


def relative_air_speed(v_ms: float, bearing_deg: float, env: Environment) -> float:
    """Calculate relative air speed accounting for wind.

    Computes the magnitude of the relative wind velocity vector:
    v_rel = v * direction_hat - wind_vector

    Args:
        v_ms: Rider speed in m/s.
        bearing_deg: Direction of travel in degrees (0° = North, 90° = East).
        env: Environmental conditions including wind components.

    Returns:
        Magnitude of relative air speed in m/s.

    Example:
        >>> env = Environment(air_density=1.225, wind_u_ms=2.0, wind_v_ms=0.0)
        >>> # Riding east at 10 m/s with 2 m/s eastward wind
        >>> v_rel = relative_air_speed(10.0, 90.0, env)
        >>> round(v_rel, 1)
        8.0
    """
    bearing_rad = math.radians(bearing_deg)

    # Unit direction vector (t_hat)
    direction_east = math.sin(bearing_rad)
    direction_north = math.cos(bearing_rad)

    # Rider velocity components
    velocity_east = v_ms * direction_east
    velocity_north = v_ms * direction_north

    # Relative air velocity = rider velocity - wind velocity
    relative_east = velocity_east - env.wind_u_ms
    relative_north = velocity_north - env.wind_v_ms

    return math.hypot(relative_east, relative_north)


def power_required(
    v_ms: float,
    slope_tan: float,
    bearing_deg: float,
    rb: RiderBike,
    env: Environment,
    acc_ms2: float = 0.0,
) -> float:
    """Calculate power required to maintain speed on given terrain.

    Implements the cycling power model from Martin et al. (1998):
    P = (P_gravity + P_rolling + P_aero + P_acceleration) / efficiency

    Args:
        v_ms: Speed in m/s.
        slope_tan: Slope as tangent (rise/run), not percentage.
        bearing_deg: Direction of travel in degrees (0° = North).
        rb: Rider and bike characteristics.
        env: Environmental conditions.
        acc_ms2: Acceleration in m/s², defaults to 0.0.

    Returns:
        Required power in watts (non-negative).

    Example:
        >>> rb = RiderBike(
        ...     mass_rider_kg=72.0, mass_bike_kg=8.0, crr=0.0035, cda=0.30, drivetrain_eff=0.97
        ... )
        >>> env = Environment(air_density=1.225)
        >>> # 10 m/s on flat ground
        >>> power = power_required(10.0, 0.0, 0.0, rb, env)
        >>> 150 < power < 200  # Typical range for these conditions
        True

    References:
        Martin, J. C., et al. (1998). "Validation of a Mathematical Model for
        Road Cycling Power." Journal of Applied Biomechanics, 14(3), 276-291.
    """
    slope_angle_rad = math.atan(slope_tan)
    total_mass = rb.mass_system_kg
    air_density = env.air_density
    v_rel = relative_air_speed(v_ms, bearing_deg, env)

    # Power components (watts)
    power_gravity = total_mass * GRAVITY * v_ms * math.sin(slope_angle_rad)
    power_rolling = rb.crr * total_mass * GRAVITY * v_ms * math.cos(slope_angle_rad)
    power_aero = 0.5 * air_density * rb.cda * (v_rel**3)
    power_acceleration = total_mass * acc_ms2 * v_ms

    # Total power accounting for drivetrain losses
    power_total = (
        power_gravity + power_rolling + power_aero + power_acceleration
    ) / rb.drivetrain_eff

    return max(0.0, power_total)


def speed_from_power(
    power_w: float,
    slope_tan: float,
    bearing_deg: float,
    rb: RiderBike,
    env: Environment,
) -> float:
    """Calculate speed achievable with given power output.

    Solves the inverse problem of `power_required` using bisection method.

    Args:
        power_w: Available power in watts.
        slope_tan: Slope as tangent (rise/run).
        bearing_deg: Direction of travel in degrees.
        rb: Rider and bike characteristics.
        env: Environmental conditions.

    Returns:
        Achievable speed in m/s.

    Example:
        >>> rb = RiderBike(
        ...     mass_rider_kg=72.0, mass_bike_kg=8.0, crr=0.0035, cda=0.30, drivetrain_eff=0.97
        ... )
        >>> env = Environment(air_density=1.225)
        >>> # What speed can 200W achieve on flat ground?
        >>> speed = speed_from_power(200.0, 0.0, 0.0, rb, env)
        >>> 9.0 < speed < 11.0  # Typical range
        True
    """
    # Search bounds: 0 to ~60 km/h (16.67 m/s)
    v_low = 0.0
    v_high = 60.0 / 3.6

    # Bisection method (50 iterations gives ~1e-15 precision)
    for _ in range(50):
        v_mid = 0.5 * (v_low + v_high)
        power_mid = power_required(v_mid, slope_tan, bearing_deg, rb, env)

        if power_mid > power_w:
            v_high = v_mid
        else:
            v_low = v_mid

    return 0.5 * (v_low + v_high)
