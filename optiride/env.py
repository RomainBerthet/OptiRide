import math

def air_density_kg_m3(temperature_c: float, pressure_pa: float, humidity_frac: float = 0.0):
    """
    Calcule la densité de l'air avec humidité (approx).
    - temperature_c : température en °C
    - pressure_pa   : pression en Pa
    - humidity_frac : 0..1 (relatif)
    """
    T = temperature_c + 273.15
    # Pression vapeur saturation (Tetens)
    p_ws = 610.94 * math.exp((17.625*temperature_c)/(temperature_c+243.04))  # Pa
    p_w  = humidity_frac * p_ws
    p_d  = pressure_pa - p_w
    R_d, R_w = 287.058, 461.495
    rho = p_d/(R_d*T) + p_w/(R_w*T)
    return rho
