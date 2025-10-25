"""Bicycle equipment database with aerodynamic and performance characteristics.

This module provides a comprehensive database of bicycle types, wheel configurations,
and riding positions with their associated CdA (drag area), mass, and rolling
resistance values based on published wind tunnel data and field testing.

References:
    - Chung, J. (2016). "Bicycle Rolling Resistance and Aerodynamics"
    - Blocken, B., et al. (2018). "Aerodynamic drag in cycling"
    - Various manufacturers' published data
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union


class BikeType(str, Enum):
    """Bicycle categories with typical characteristics."""

    ROAD_RACE = "road_race"  # Lightweight racing bike
    ROAD_ENDURANCE = "road_endurance"  # Comfort-oriented road bike
    AERO_ROAD = "aero_road"  # Aerodynamic road bike
    TIME_TRIAL = "time_trial"  # TT/Triathlon bike
    GRAVEL = "gravel"  # Gravel/all-road bike
    MOUNTAIN = "mountain"  # Mountain bike (XC)


class RidingPosition(str, Enum):
    """Rider position affecting CdA."""

    UPRIGHT = "upright"  # Hands on hoods, relaxed
    DROPS = "drops"  # Hands in drops
    AERO_HOODS = "aero_hoods"  # Hands on hoods, tucked
    TIME_TRIAL = "time_trial"  # TT position on aerobars
    SUPER_TUCK = "super_tuck"  # Extreme aero (descending)


class WheelType(str, Enum):
    """Wheel configurations affecting aerodynamics and mass."""

    SHALLOW_ALLOY = "shallow_alloy"  # <30mm alloy wheels
    SHALLOW_CARBON = "shallow_carbon"  # <30mm carbon wheels
    MID_DEPTH = "mid_depth"  # 40-50mm carbon
    DEEP_SECTION = "deep_section"  # 60-80mm carbon
    DISC_REAR = "disc_rear"  # Disc wheel rear


@dataclass(frozen=True)
class BikeSpec:
    """Complete bicycle specification with performance characteristics.

    Attributes:
        bike_type: Type of bicycle.
        mass_kg: Total bike mass in kilograms (frame + components).
        base_cda: Base CdA (m²) for bike alone (without rider).
        crr: Coefficient of rolling resistance.
        drivetrain_efficiency: Mechanical efficiency (0-1).
        description: Human-readable description.
    """

    bike_type: BikeType
    mass_kg: float
    base_cda: float
    crr: float
    drivetrain_efficiency: float
    description: str


@dataclass(frozen=True)
class PositionSpec:
    """Rider position aerodynamic characteristics.

    Attributes:
        position: Riding position.
        rider_cda: Additional CdA (m²) contributed by rider in this position.
        description: Human-readable description.
    """

    position: RidingPosition
    rider_cda: float
    description: str


@dataclass(frozen=True)
class WheelSpec:
    """Wheel configuration characteristics.

    Attributes:
        wheel_type: Type of wheels.
        mass_delta_kg: Mass difference vs. baseline wheels.
        cda_delta: CdA difference vs. baseline wheels (negative = faster).
        crr_delta: Crr difference vs. baseline wheels.
        description: Human-readable description.
    """

    wheel_type: WheelType
    mass_delta_kg: float
    cda_delta: float
    crr_delta: float
    description: str


# Comprehensive bike database
BIKE_DATABASE: dict[BikeType, BikeSpec] = {
    BikeType.ROAD_RACE: BikeSpec(
        bike_type=BikeType.ROAD_RACE,
        mass_kg=7.5,
        base_cda=0.08,
        crr=0.0035,
        drivetrain_efficiency=0.977,
        description="Lightweight racing bike (e.g., Specialized Tarmac, Trek Émonda)",
    ),
    BikeType.ROAD_ENDURANCE: BikeSpec(
        bike_type=BikeType.ROAD_ENDURANCE,
        mass_kg=8.5,
        base_cda=0.09,
        crr=0.004,
        drivetrain_efficiency=0.975,
        description="Comfort road bike (e.g., Specialized Roubaix, Trek Domane)",
    ),
    BikeType.AERO_ROAD: BikeSpec(
        bike_type=BikeType.AERO_ROAD,
        mass_kg=8.2,
        base_cda=0.07,
        crr=0.0035,
        drivetrain_efficiency=0.977,
        description="Aerodynamic road bike (e.g., Cervélo S5, Venge)",
    ),
    BikeType.TIME_TRIAL: BikeSpec(
        bike_type=BikeType.TIME_TRIAL,
        mass_kg=9.0,
        base_cda=0.06,
        crr=0.003,
        drivetrain_efficiency=0.977,
        description="Time trial/triathlon bike with aerobars",
    ),
    BikeType.GRAVEL: BikeSpec(
        bike_type=BikeType.GRAVEL,
        mass_kg=9.5,
        base_cda=0.10,
        crr=0.006,
        drivetrain_efficiency=0.97,
        description="Gravel/all-road bike with wider tires",
    ),
    BikeType.MOUNTAIN: BikeSpec(
        bike_type=BikeType.MOUNTAIN,
        mass_kg=11.0,
        base_cda=0.12,
        crr=0.008,
        drivetrain_efficiency=0.95,
        description="Cross-country mountain bike",
    ),
}

# Rider position database (CdA values for ~75kg rider, ~1.80m height)
POSITION_DATABASE: dict[RidingPosition, PositionSpec] = {
    RidingPosition.UPRIGHT: PositionSpec(
        position=RidingPosition.UPRIGHT,
        rider_cda=0.35,
        description="Hands on hoods, relaxed upright position",
    ),
    RidingPosition.DROPS: PositionSpec(
        position=RidingPosition.DROPS,
        rider_cda=0.28,
        description="Hands in drops, moderately aggressive",
    ),
    RidingPosition.AERO_HOODS: PositionSpec(
        position=RidingPosition.AERO_HOODS,
        rider_cda=0.30,
        description="Hands on hoods, elbows tucked",
    ),
    RidingPosition.TIME_TRIAL: PositionSpec(
        position=RidingPosition.TIME_TRIAL,
        rider_cda=0.22,
        description="On aerobars, full TT position",
    ),
    RidingPosition.SUPER_TUCK: PositionSpec(
        position=RidingPosition.SUPER_TUCK,
        rider_cda=0.18,
        description="Extreme aero position (descending)",
    ),
}

# Wheel configuration database (deltas relative to baseline shallow wheels)
WHEEL_DATABASE: dict[WheelType, WheelSpec] = {
    WheelType.SHALLOW_ALLOY: WheelSpec(
        wheel_type=WheelType.SHALLOW_ALLOY,
        mass_delta_kg=0.0,
        cda_delta=0.0,
        crr_delta=0.0,
        description="Baseline: shallow alloy clinchers (<30mm)",
    ),
    WheelType.SHALLOW_CARBON: WheelSpec(
        wheel_type=WheelType.SHALLOW_CARBON,
        mass_delta_kg=-0.4,
        cda_delta=-0.002,
        crr_delta=-0.0002,
        description="Shallow carbon wheels (<30mm)",
    ),
    WheelType.MID_DEPTH: WheelSpec(
        wheel_type=WheelType.MID_DEPTH,
        mass_delta_kg=-0.2,
        cda_delta=-0.008,
        crr_delta=-0.0003,
        description="Mid-depth carbon (40-50mm)",
    ),
    WheelType.DEEP_SECTION: WheelSpec(
        wheel_type=WheelType.DEEP_SECTION,
        mass_delta_kg=0.1,
        cda_delta=-0.012,
        crr_delta=-0.0003,
        description="Deep-section carbon (60-80mm)",
    ),
    WheelType.DISC_REAR: WheelSpec(
        wheel_type=WheelType.DISC_REAR,
        mass_delta_kg=0.3,
        cda_delta=-0.015,
        crr_delta=-0.0003,
        description="Disc wheel rear + deep front",
    ),
}


def get_bike_config(
    bike_type: Union[BikeType, str],
    position: Union[RidingPosition, str, None] = None,
    wheels: Union[WheelType, str, None] = None,
    rider_height_m: Union[float, None] = None,
    rider_mass_kg: Union[float, None] = None,
) -> dict[str, float]:
    """Get complete bike configuration with computed CdA, mass, and Crr.

    The rider's CdA is automatically adjusted based on height and mass if provided.
    If not provided, reference values (1.80m, 75kg) are used.

    Args:
        bike_type: Type of bicycle (enum or string).
        position: Rider position (enum or string). Defaults to DROPS for road bikes,
            TIME_TRIAL for TT bikes.
        wheels: Wheel type (enum or string). Defaults to SHALLOW_ALLOY.
        rider_height_m: Rider height in meters. If provided, CdA is scaled accordingly.
        rider_mass_kg: Rider mass in kg. If provided, CdA is scaled accordingly.

    Returns:
        Dictionary with keys: mass_kg, cda, crr, drivetrain_efficiency.

    Raises:
        KeyError: If bike_type, position, or wheels not found in database.

    Example:
        >>> # Default reference rider (1.80m, 75kg)
        >>> config = get_bike_config("aero_road", "drops", "deep_section")
        >>> config["cda"]  # doctest: +SKIP
        0.340
        >>> # Adjusted for specific rider
        >>> config = get_bike_config(
        ...     "aero_road", "drops", "deep_section", rider_height_m=1.75, rider_mass_kg=68.0
        ... )
        >>> config["cda"]  # doctest: +SKIP
        0.325
    """
    # Convert strings to enums if needed
    if isinstance(bike_type, str):
        bike_type = BikeType(bike_type)
    if isinstance(position, str):
        position = RidingPosition(position)
    if isinstance(wheels, str):
        wheels = WheelType(wheels)

    # Get base bike spec
    bike_spec = BIKE_DATABASE[bike_type]

    # Default position based on bike type
    if position is None:
        if bike_type == BikeType.TIME_TRIAL:
            position = RidingPosition.TIME_TRIAL
        else:
            position = RidingPosition.DROPS

    # Default wheels
    if wheels is None:
        wheels = WheelType.SHALLOW_ALLOY

    # Get position and wheel specs
    position_spec = POSITION_DATABASE[position]
    wheel_spec = WHEEL_DATABASE[wheels]

    # Adjust rider CdA based on height and mass if provided
    rider_cda = position_spec.rider_cda
    if rider_height_m is not None and rider_mass_kg is not None:
        rider_cda = estimate_cda_from_height_mass(rider_height_m, rider_mass_kg, position)
    elif rider_height_m is not None or rider_mass_kg is not None:
        # If only one is provided, use it with reference value for the other
        height = rider_height_m if rider_height_m is not None else 1.80
        mass = rider_mass_kg if rider_mass_kg is not None else 75.0
        rider_cda = estimate_cda_from_height_mass(height, mass, position)

    # Compute final values
    total_cda = bike_spec.base_cda + rider_cda + wheel_spec.cda_delta
    total_mass = bike_spec.mass_kg + wheel_spec.mass_delta_kg
    total_crr = bike_spec.crr + wheel_spec.crr_delta

    return {
        "mass_kg": total_mass,
        "cda": total_cda,
        "crr": total_crr,
        "drivetrain_efficiency": bike_spec.drivetrain_efficiency,
    }


def list_bike_types() -> list[str]:
    """Get list of available bike types.

    Returns:
        List of bike type identifiers.
    """
    return [bt.value for bt in BikeType]


def list_positions() -> list[str]:
    """Get list of available riding positions.

    Returns:
        List of position identifiers.
    """
    return [pos.value for pos in RidingPosition]


def list_wheel_types() -> list[str]:
    """Get list of available wheel types.

    Returns:
        List of wheel type identifiers.
    """
    return [wt.value for wt in WheelType]


def estimate_cda_from_height_mass(
    height_m: float,
    mass_kg: float,
    position: Union[RidingPosition, str] = RidingPosition.DROPS,
) -> float:
    """Estimate rider CdA based on anthropometric data.

    Uses empirical scaling based on frontal area estimation.
    Reference: frontal_area ≈ 0.0293 * height^0.725 * mass^0.425 (DuBois formula)

    Args:
        height_m: Rider height in meters.
        mass_kg: Rider mass in kilograms.
        position: Riding position.

    Returns:
        Estimated CdA in m².

    Example:
        >>> cda = estimate_cda_from_height_mass(1.80, 75.0, "drops")
        >>> 0.25 < cda < 0.35
        True
    """
    if isinstance(position, str):
        position = RidingPosition(position)

    # Reference: 1.80m, 75kg rider
    reference_height = 1.80
    reference_mass = 75.0
    reference_cda = POSITION_DATABASE[position].rider_cda

    # DuBois-style scaling for frontal area
    height_factor = (height_m / reference_height) ** 0.725
    mass_factor = (mass_kg / reference_mass) ** 0.425

    return reference_cda * height_factor * mass_factor


def get_simple_config(
    bike_type: str = "aero_road",
    position: str = "drops",
) -> dict[str, float]:
    """Get bike configuration with sensible defaults for quick setup.

    Args:
        bike_type: Type of bicycle. Defaults to "aero_road".
        position: Riding position. Defaults to "drops".

    Returns:
        Configuration dictionary with mass_kg, cda, crr, drivetrain_efficiency.

    Example:
        >>> config = get_simple_config()
        >>> config["cda"]  # doctest: +SKIP
        0.35
    """
    # Use mid-depth wheels as good all-around choice
    return get_bike_config(bike_type, position, WheelType.MID_DEPTH)
