"""OptiRide: Professional cycling pacing optimizer.

This package provides tools for optimizing cycling pacing strategies from GPX data,
including power targets, nutrition planning, and start time optimization based on
weather conditions.
"""

from optiride.models import Environment, RiderBike
from optiride.optimizer import pace_heuristic, simulate
from optiride.physics import power_required, speed_from_power

__version__ = "0.1.0"
__author__ = "Romain BERTHET"
__email__ = "berthet.romain3@gmail.com"

__all__ = [
    "Environment",
    "RiderBike",
    "pace_heuristic",
    "power_required",
    "simulate",
    "speed_from_power",
]
