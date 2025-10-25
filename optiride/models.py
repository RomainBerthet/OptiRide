from dataclasses import dataclass
from typing import Optional

@dataclass
class RiderBike:
    mass_rider_kg: float
    mass_bike_kg: float
    crr: float
    cda: float
    drivetrain_eff: float = 0.97
    cp: Optional[float] = None
    w_prime_j: Optional[float] = None  # en Joules
    ftp: Optional[float] = None
    age: Optional[int] = None

    @property
    def mass_system_kg(self) -> float:
        return self.mass_rider_kg + self.mass_bike_kg

@dataclass
class Environment:
    air_density: float
    wind_u_ms: float = 0.0
    wind_v_ms: float = 0.0
