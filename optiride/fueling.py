"""Advanced fueling and fatigue management for cycling.

Calculates optimal refueling points based on energy expenditure, ride duration,
and physiological constraints. Includes W' balance modeling for fatigue tracking.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class FuelingPoint:
    """Represents a fueling/refueling point during the ride.

    Attributes:
        distance_km: Distance from start in kilometers.
        time_h: Time from start in hours.
        carbs_g: Carbohydrates to consume (grams).
        fluids_ml: Fluid to consume (milliliters).
        sodium_mg: Sodium to consume (milligrams).
        energy_deficit_kcal: Cumulative energy deficit at this point.
        w_prime_balance_pct: Remaining W' capacity (percentage).
        fatigue_index: Fatigue level (0-100, higher = more tired).
        refuel_type: Type of nutrition ("gel", "bar", "drink", "solid").
        notes: Additional recommendations.
    """

    distance_km: float
    time_h: float
    carbs_g: float
    fluids_ml: float
    sodium_mg: float
    energy_deficit_kcal: float
    w_prime_balance_pct: float
    fatigue_index: float
    refuel_type: str
    notes: str


def calculate_power_zones(ftp: float) -> dict[str, tuple[float, float]]:
    """Calculate personalized power zones based on FTP.

    Uses the standard 7-zone model (Coggan) adapted for endurance cycling.

    Args:
        ftp: Functional Threshold Power in watts.

    Returns:
        Dictionary mapping zone names to (min, max) power ranges in watts.

    Example:
        >>> zones = calculate_power_zones(260)
        >>> zones["tempo"]
        (195.0, 234.0)
    """
    return {
        "recovery": (0.0, ftp * 0.55),  # Zone 1: Active recovery
        "endurance": (ftp * 0.55, ftp * 0.75),  # Zone 2: Aerobic endurance
        "tempo": (ftp * 0.75, ftp * 0.90),  # Zone 3: Tempo
        "threshold": (ftp * 0.90, ftp * 1.05),  # Zone 4: Lactate threshold
        "vo2max": (ftp * 1.05, ftp * 1.20),  # Zone 5: VO2max
        "anaerobic": (ftp * 1.20, float("inf")),  # Zone 6+: Anaerobic
    }


def get_power_zone_name(power: float, ftp: float) -> str:
    """Get the power zone name for a given power value.

    Args:
        power: Power in watts.
        ftp: Functional Threshold Power in watts.

    Returns:
        Zone name as string.

    Example:
        >>> get_power_zone_name(200, 260)
        'tempo'
    """
    zones = calculate_power_zones(ftp)
    for name, (min_p, max_p) in zones.items():
        if min_p <= power < max_p:
            return name
    return "anaerobic"


def calculate_w_prime_balance(
    powers: np.ndarray,
    times_s: np.ndarray,
    cp: float,
    w_prime: float,
    tau: float = 546.0,
) -> np.ndarray:
    """Calculate W' balance (anaerobic work capacity) throughout the ride.

    Uses the differential W' balance model (Skiba et al., 2012).

    Args:
        powers: Power values in watts.
        times_s: Time values in seconds.
        cp: Critical Power in watts.
        w_prime: Anaerobic work capacity (W') in joules.
        tau: Time constant for W' recovery (seconds), typically 300-600s.

    Returns:
        Array of W' balance values (0-1, where 1 = fully recovered).

    References:
        Skiba, P. F., et al. (2012). "Modeling the expenditure and reconstitution
        of work capacity above critical power." Medicine & Science in Sports &
        Exercise, 44(8), 1526-1532.
    """
    if cp is None or w_prime is None:
        # Return constant 100% if no CP/W' data
        return np.ones_like(powers)

    w_bal = np.zeros_like(powers, dtype=float)
    w_bal[0] = w_prime  # Start fully recovered

    for i in range(1, len(powers)):
        dt = times_s[i] - times_s[i - 1]
        power_above_cp = max(0, powers[i - 1] - cp)

        if power_above_cp > 0:
            # Expenditure: working above CP
            w_bal[i] = w_bal[i - 1] - power_above_cp * dt
        else:
            # Recovery: working below CP
            power_below_cp = cp - powers[i - 1]
            recovery = power_below_cp * (w_prime - w_bal[i - 1]) * dt / tau / w_prime
            w_bal[i] = w_bal[i - 1] + recovery

        # Clamp to valid range
        w_bal[i] = np.clip(w_bal[i], 0, w_prime)

    # Convert to percentage
    return w_bal / w_prime


def calculate_fatigue_index(
    w_prime_balance_pct: float,
    time_h: float,
    intensity_factor: float,
) -> float:
    """Calculate fatigue index based on multiple factors.

    Args:
        w_prime_balance_pct: Remaining W' capacity (0-1).
        time_h: Elapsed time in hours.
        intensity_factor: Average power / FTP.

    Returns:
        Fatigue index 0-100 (0 = fresh, 100 = exhausted).

    Example:
        >>> calculate_fatigue_index(0.5, 3.0, 0.85)
        65.0
    """
    # W' depletion contributes to fatigue
    w_fatigue = (1.0 - w_prime_balance_pct) * 40

    # Duration fatigue (increases non-linearly)
    duration_fatigue = min(40, time_h**1.5 * 8)

    # Intensity fatigue
    intensity_fatigue = max(0, (intensity_factor - 0.6) * 40)

    total_fatigue = w_fatigue + duration_fatigue + intensity_fatigue
    return float(np.clip(total_fatigue, 0, 100))


def calculate_fueling_points(
    distances_km: np.ndarray,
    times_h: np.ndarray,
    powers_w: np.ndarray,
    ftp: float,
    cp: Optional[float] = None,
    w_prime: Optional[float] = None,
    refuel_interval_min: float = 20.0,
    carbs_per_hour: float = 60.0,
) -> list[FuelingPoint]:
    """Calculate optimal fueling points during the ride.

    Args:
        distances_km: Distance array in kilometers.
        times_h: Time array in hours.
        powers_w: Power array in watts.
        ftp: Functional Threshold Power in watts.
        cp: Critical Power in watts (optional).
        w_prime: Anaerobic work capacity in joules (optional).
        refuel_interval_min: Minimum interval between refueling (minutes).
        carbs_per_hour: Target carbohydrate intake (g/h).

    Returns:
        List of FuelingPoint objects with recommendations.

    Example:
        >>> dists = np.array([0, 10, 20, 30])
        >>> times = np.array([0, 0.5, 1.0, 1.5])
        >>> powers = np.array([200, 220, 240, 260])
        >>> points = calculate_fueling_points(dists, times, powers, 260)
        >>> len(points) > 0
        True
    """
    if len(distances_km) == 0:
        return []

    total_duration_h = times_h[-1]
    if total_duration_h < 0.5:  # Less than 30 min, no refueling needed
        return []

    # Calculate W' balance if CP/W' available
    if cp is not None and w_prime is not None:
        times_s: np.ndarray = times_h * 3600
        w_balance_pct = calculate_w_prime_balance(powers_w, times_s, cp, w_prime)
    else:
        w_balance_pct = np.ones_like(powers_w)

    # Calculate cumulative energy expenditure
    if len(times_h) > 1:
        dt_h = np.diff(times_h)
        dt_h = np.append(dt_h, dt_h[-1])  # Extend for last point
    else:
        dt_h = np.array([0.0])

    energy_kcal = np.cumsum(powers_w * dt_h * 3600 / 4184 / 0.22)  # 22% efficiency

    # Calculate intensity factor
    avg_power = np.mean(powers_w[powers_w > 0])
    intensity_factor = avg_power / ftp if ftp > 0 else 0.75

    # Determine refueling points
    refuel_interval_h = refuel_interval_min / 60.0
    num_refuel = int(total_duration_h / refuel_interval_h)

    fueling_points = []

    for i in range(1, num_refuel + 1):
        target_time_h = i * refuel_interval_h

        # Find closest index
        idx = np.argmin(np.abs(times_h - target_time_h))

        distance_km = float(distances_km[idx])
        time_h = float(times_h[idx])
        w_bal_pct = float(w_balance_pct[idx])
        energy_deficit = float(energy_kcal[idx])

        # Calculate fatigue
        fatigue = calculate_fatigue_index(w_bal_pct, time_h, intensity_factor)

        # Determine refuel amount and type
        carbs_g = carbs_per_hour * refuel_interval_h

        # Adjust based on intensity and fatigue
        if fatigue > 70:
            # High fatigue: prefer quick carbs (gels)
            refuel_type = "gel"
            carbs_g *= 1.2  # Increase intake
            notes = "⚠️ Fatigue élevée - Glucides rapides recommandés"
        elif time_h < 1.0:
            # Early ride: bars/solids OK
            refuel_type = "bar"
            notes = "🍫 Début de sortie - Solides OK"
        elif intensity_factor > 0.85:
            # High intensity: prefer liquids
            refuel_type = "drink"
            notes = "⚡ Intensité élevée - Boisson énergétique"
        else:
            # Moderate: mix of options
            refuel_type = "bar" if i % 2 == 0 else "gel"
            notes = "💪 Rythme modéré - Mixte solide/gel"

        # Fluids and sodium
        fluids_ml = 600 * refuel_interval_h / 1.0  # ~600ml/h
        sodium_mg = 500 * refuel_interval_h / 1.0  # ~500mg/h

        # Add special notes
        if w_bal_pct < 0.3:
            notes += " | 🔋 W' faible - Réduire l'effort"
        elif distance_km > distances_km[-1] * 0.8:
            notes += " | 🏁 Proche de l'arrivée - Dernier effort"

        fueling_points.append(
            FuelingPoint(
                distance_km=distance_km,
                time_h=time_h,
                carbs_g=carbs_g,
                fluids_ml=fluids_ml,
                sodium_mg=sodium_mg,
                energy_deficit_kcal=energy_deficit,
                w_prime_balance_pct=w_bal_pct,
                fatigue_index=fatigue,
                refuel_type=refuel_type,
                notes=notes,
            )
        )

    return fueling_points
