import requests
from typing import Optional, Dict

def fetch_open_meteo(lat: float, lon: float, hour_utc_index: Optional[int] = None) -> Dict:
    """
    Récupère météo horaire depuis Open-Meteo pour lat/lon.
    hour_utc_index: index d'heure dans la série (None => 0)
    Retourne dict avec: temperature_C, humidity_frac, pressure_Pa, wind_speed_mps, wind_dir_deg
    """
    # On demande les variables nécessaires (température, humidité, vent, pression MSL)
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,pressure_msl"
        "&windspeed_unit=ms&timezone=UTC"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    h = data["hourly"]
    idx = hour_utc_index if hour_utc_index is not None else 0

    temp = float(h["temperature_2m"][idx])
    rh = float(h["relative_humidity_2m"][idx]) / 100.0
    wspd = float(h["wind_speed_10m"][idx])
    wdir = float(h["wind_direction_10m"][idx])
    p_pa = float(h["pressure_msl"][idx]) * 100.0  # hPa -> Pa

    return dict(
        temperature_C=temp,
        humidity_frac=rh,
        pressure_Pa=p_pa,
        wind_speed_mps=wspd,
        wind_dir_deg=wdir
    )

def met_wdir_to_uv(speed_mps: float, dir_deg_from: float):
    """
    Convertit direction météo (d'où vient le vent, en ° depuis le nord) en composantes (u,v) m/s.
    u = vers l'est, v = vers le nord.
    """
    import math
    rad = math.radians(dir_deg_from)
    u = -speed_mps * math.sin(rad)
    v = -speed_mps * math.cos(rad)
    return u, v
