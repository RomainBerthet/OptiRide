"""Data models for rider, bike, and environmental conditions."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RiderBike:
    """Represents a rider and bike system with physical and performance characteristics.

    This class encapsulates all the physical parameters needed to model cycling
    performance, including mass, aerodynamics, rolling resistance, and power capabilities.

    Attributes:
        mass_rider_kg: Rider mass in kilograms.
        mass_bike_kg: Bike mass in kilograms.
        crr: Coefficient of rolling resistance (dimensionless, typically 0.002-0.005).
        cda: Aerodynamic drag area in m² (CdA, typically 0.2-0.4 for road cycling).
        drivetrain_eff: Drivetrain efficiency (0-1, typically 0.95-0.98).
        cp: Critical Power in watts (sustained power threshold).
        w_prime_j: W' (W-prime) in joules, anaerobic work capacity above CP.
        ftp: Functional Threshold Power in watts (alternative to CP).
        age: Rider age in years (optional, for physiological calculations).

    Example:
        >>> rider = RiderBike(
        ...     mass_rider_kg=72.0,
        ...     mass_bike_kg=8.0,
        ...     crr=0.0035,
        ...     cda=0.30,
        ...     ftp=260.0,
        ...     w_prime_j=20000.0,
        ... )
        >>> rider.mass_system_kg
        80.0
    """

    mass_rider_kg: float
    mass_bike_kg: float
    crr: float
    cda: float
    drivetrain_eff: float = 0.97
    cp: Optional[float] = None
    w_prime_j: Optional[float] = None
    ftp: Optional[float] = None
    age: Optional[int] = None

    @property
    def mass_system_kg(self) -> float:
        """Total system mass (rider + bike) in kilograms.

        Returns:
            Combined mass of rider and bike.
        """
        return self.mass_rider_kg + self.mass_bike_kg


@dataclass
class Environment:
    """Environmental conditions affecting cycling performance.

    This class represents atmospheric and wind conditions that impact aerodynamic
    drag and overall cycling performance.

    Attributes:
        air_density: Air density in kg/m³ (typically 1.1-1.3, varies with
            temperature, pressure, and humidity).
        wind_u_ms: East-west wind component in m/s (positive = eastward).
        wind_v_ms: North-south wind component in m/s (positive = northward).

    Example:
        >>> env = Environment(air_density=1.225, wind_u_ms=2.0, wind_v_ms=-1.0)
    """

    air_density: float
    wind_u_ms: float = 0.0
    wind_v_ms: float = 0.0
