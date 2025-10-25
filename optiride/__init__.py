"""OptiRide: Professional cycling pacing optimizer.

This package provides tools for optimizing cycling pacing strategies from GPX data,
including power targets, nutrition planning, and start time optimization based on
weather conditions.

Features a comprehensive bike database to simplify configuration - just specify your
GPX trace, weight, and FTP. The library automatically configures bike specifications.

Example:
    >>> import optiride as opr
    >>> from optiride.bike_library import get_bike_config
    >>>
    >>> # Get bike configuration from library
    >>> bike_config = get_bike_config("aero_road", "drops")
    >>>
    >>> rider = opr.RiderBike(
    ...     mass_rider_kg=72.0,
    ...     mass_bike_kg=bike_config["mass_kg"],
    ...     cda=bike_config["cda"],
    ...     crr=bike_config["crr"],
    ...     ftp=260.0,
    ... )
    >>> env = opr.Environment(air_density=1.225)
    >>> power = opr.power_required(10.0, 0.05, 0.0, rider, env)
"""

from optiride.bike_library import (
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
from optiride.models import Environment, RiderBike
from optiride.optimizer import pace_heuristic, simulate
from optiride.physics import power_required, relative_air_speed, speed_from_power

__version__ = "0.1.0"
__author__ = "Romain BERTHET"
__email__ = "berthet.romain3@gmail.com"

__all__ = [
    # Bike library
    "BikeType",
    # Core models
    "Environment",
    "RiderBike",
    "RidingPosition",
    "WheelType",
    "estimate_cda_from_height_mass",
    "get_bike_config",
    "get_simple_config",
    "list_bike_types",
    "list_positions",
    "list_wheel_types",
    # Optimizer
    "pace_heuristic",
    # Physics
    "power_required",
    "relative_air_speed",
    "simulate",
    "speed_from_power",
]
