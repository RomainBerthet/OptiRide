import numpy as np

from .models import Environment, RiderBike
from .physics import speed_from_power


def pace_heuristic(
    dist_m: np.ndarray,
    slope: np.ndarray,
    bearings_deg: np.ndarray,
    rb: RiderBike,
    env: Environment,
    P_flat: float,
    up_mult: float = 1.10,
    down_mult: float = 0.75,
    max_delta_w: float = 30.0,
):
    P = np.full_like(slope, P_flat, dtype=float)
    P[slope > 0.02] *= up_mult
    P[slope < -0.02] *= down_mult
    # lissage
    for i in range(1, len(P)):
        lo = P[i - 1] - max_delta_w
        hi = P[i - 1] + max_delta_w
        P[i] = min(max(P[i], lo), hi)
    # simple garde-fou CP/W'
    if rb.cp and rb.w_prime_j:
        ds = dist_m[1] - dist_m[0]
        # estimation dt ~ ds / v (supposons 8 m/s ~ 28.8 km/h pour initialisation)
        dt_guess = ds / 8.0
        wbal = rb.w_prime_j
        cp = rb.cp
        for i in range(len(P)):
            p = P[i]
            if p > cp:
                wbal = max(0.0, wbal - (p - cp) * dt_guess)
                if wbal <= 0.0:
                    P[i] = cp
            else:
                wbal = min(rb.w_prime_j, wbal + (cp - p) * 0.3 * dt_guess)
    return P


def simulate(
    dist_m: np.ndarray,
    slope: np.ndarray,
    bearings_deg: np.ndarray,
    P_target: np.ndarray,
    rb: RiderBike,
    env: Environment,
):
    ds = dist_m[1] - dist_m[0]
    v = np.zeros_like(P_target)
    dt = np.zeros_like(P_target)
    for i in range(len(P_target)):
        v[i] = speed_from_power(
            float(P_target[i]), float(slope[i]), float(bearings_deg[i]), rb, env
        )
        dt[i] = ds / max(0.01, v[i])
    T = dt.sum()
    work_J = float(np.sum(P_target * dt))
    return v, dt, T, work_J
