import math
from .models import RiderBike, Environment

g = 9.80665

def relative_air_speed(v_ms: float, bearing_deg: float, env: Environment) -> float:
    """
    Calcule la norme de la vitesse de l'air relative:
    v_rel_vec = v * t_hat - wind_vec
    où t_hat est le vecteur unitaire du segment selon le cap (bearing).
    wind_vec = (u_east, v_north).
    """
    br = math.radians(bearing_deg)
    t_x = math.sin(br)  # est
    t_y = math.cos(br)  # nord
    vx = v_ms * t_x
    vy = v_ms * t_y
    rx = vx - getattr(env, "wind_u_ms", 0.0)
    ry = vy - getattr(env, "wind_v_ms", 0.0)
    return math.hypot(rx, ry)

def power_required(v_ms: float, slope_tan: float, bearing_deg: float, rb: RiderBike, env: Environment, acc_ms2: float = 0.0) -> float:
    theta = math.atan(slope_tan)
    m = rb.mass_system_kg
    rho = env.air_density
    v_rel = relative_air_speed(v_ms, bearing_deg, env)
    Pg   = m*g*v_ms*math.sin(theta)
    Prr  = rb.crr*m*g*v_ms*math.cos(theta)
    Pa   = 0.5*rho*rb.cda*(v_rel**3)
    Pacc = m*acc_ms2*v_ms
    Ptot = (Pg + Prr + Pa + Pacc) / rb.drivetrain_eff
    return max(0.0, Ptot)

def speed_from_power(P_w: float, slope_tan: float, bearing_deg: float, rb: RiderBike, env: Environment) -> float:
    # Résout P(v)=P par bissection
    v_lo, v_hi = 0.0, 60/3.6
    for _ in range(50):
        v_mid = 0.5*(v_lo+v_hi)
        P_mid = power_required(v_mid, slope_tan, bearing_deg, rb, env)
        if P_mid > P_w: 
            v_hi = v_mid
        else:
            v_lo = v_mid
    return 0.5*(v_lo+v_hi)
