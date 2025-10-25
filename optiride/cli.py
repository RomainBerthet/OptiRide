import argparse
import datetime
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .bike_library import get_bike_config, list_bike_types, list_positions
from .env import air_density_kg_m3
from .exporter import write_power_gpx
from .gpxio import read_gpx_resample
from .models import Environment, RiderBike
from .nutrition import fueling_plan
from .optimizer import pace_heuristic, simulate
from .weather import fetch_open_meteo, met_wdir_to_uv


def _build_rb_env(args, airtemp, humidity, pressure, wind_u, wind_v):
    rho = air_density_kg_m3(airtemp, pressure, humidity)

    # Start with bike library defaults, adjusted for rider anthropometry
    bike_config = get_bike_config(
        getattr(args, "bike_type", "aero_road"),
        position=getattr(args, "position", "drops"),
        wheels=getattr(args, "wheels", None),
        rider_height_m=getattr(args, "height", None),
        rider_mass_kg=args.mass,
    )

    # Allow manual overrides (if specified, they take precedence)
    mass_bike = getattr(args, "bike_mass", None) or bike_config["mass_kg"]
    cda = getattr(args, "cda", None) or bike_config["cda"]
    crr = getattr(args, "crr", None) or bike_config["crr"]
    eff = getattr(args, "eff", None) or bike_config["drivetrain_efficiency"]

    rb = RiderBike(
        mass_rider_kg=args.mass,
        mass_bike_kg=mass_bike,
        crr=crr,
        cda=cda,
        drivetrain_eff=eff,
        cp=getattr(args, "cp", None),
        w_prime_j=getattr(args, "wprime", None),
        ftp=getattr(args, "ftp", None),
        age=getattr(args, "age", None),
    )
    env = Environment(air_density=rho, wind_u_ms=wind_u, wind_v_ms=wind_v)
    return rb, env, rho


def compute(args):
    dist, elev, slope, lat_i, lon_i, bearings = read_gpx_resample(args.gpx, step_m=args.step_m)

    # WEATHER
    weather = None
    if args.auto_weather:
        lat = float(np.mean(lat_i))
        lon = float(np.mean(lon_i))
        hour_index = None
        if args.hour is not None:
            hour_index = int(args.hour)  # simplifié
        weather = fetch_open_meteo(lat, lon, hour_utc_index=hour_index)
        airtemp = weather["temperature_C"]
        humidity = weather["humidity_frac"]
        pressure = weather["pressure_Pa"]
        wind_u, wind_v = met_wdir_to_uv(weather["wind_speed_mps"], weather["wind_dir_deg"])
    else:
        airtemp = args.airtemp
        humidity = args.humidity
        pressure = args.pressure
        wind_u, wind_v = args.wind_u, args.wind_v

    rb, env, rho = _build_rb_env(args, airtemp, humidity, pressure, wind_u, wind_v)

    P_target = pace_heuristic(
        dist,
        slope,
        bearings,
        rb,
        env,
        P_flat=args.power_flat,
        up_mult=args.up_mult,
        down_mult=args.down_mult,
        max_delta_w=args.max_delta,
    )
    v, dt, T, W = simulate(dist, slope, bearings, P_target, rb, env)
    fuel = fueling_plan(T, W, gross_eff=args.gross_eff)

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "plots"), exist_ok=True)

    df = pd.DataFrame(
        {
            "dist_m": dist,
            "elev_m": elev,
            "slope": slope,
            "bearing_deg": bearings,
            "lat": lat_i,
            "lon": lon_i,
            "P_target_W": P_target,
            "v_ms": v,
            "dt_s": dt,
            "t_cum_s": np.cumsum(dt),
        }
    )
    df.to_csv(os.path.join(args.output_dir, "targets.csv"), index=False)

    summary = dict(
        total_time_s=float(T),
        total_time_h=float(T / 3600.0),
        work_J=float(W),
        air_density=rho,
        weather=weather,
        params={k: v for k, v in vars(args).items() if k not in ["func"]},
    )
    with open(os.path.join(args.output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Plots
    plt.figure()
    plt.plot(df["dist_m"] / 1000.0, df["P_target_W"])
    plt.xlabel("Distance (km)")
    plt.ylabel("Puissance cible (W)")
    plt.title("Puissance cible vs distance")
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, "plots", "power_target.png"))

    plt.figure()
    plt.plot(df["dist_m"] / 1000.0, df["v_ms"] * 3.6)
    plt.xlabel("Distance (km)")
    plt.ylabel("Vitesse (km/h)")
    plt.title("Vitesse estimée vs distance")
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, "plots", "speed.png"))

    plt.figure()
    plt.plot(df["dist_m"] / 1000.0, df["elev_m"])
    plt.xlabel("Distance (km)")
    plt.ylabel("Altitude (m)")
    plt.title("Profil altimétrique")
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, "plots", "elevation.png"))

    # Export GPX avec puissances si demandé
    if args.export_gpx:
        start_time = None
        if args.start_time_now:
            start_time = datetime.datetime.utcnow()
        gpx_out = os.path.join(args.output_dir, "power_targets.gpx")
        write_power_gpx(
            gpx_out,
            df["lat"].values,
            df["lon"].values,
            df["elev_m"].values,
            df["P_target_W"].values,
            name="optiride-power-targets",
            start_time=start_time,
        )

    print(
        json.dumps(
            {
                "time_h": round(T / 3600.0, 3),
                "kcal": round(fuel["kcal"], 0),
                "carbs_gph": fuel["carbs_gph"],
                "liters_per_h": fuel["liters_per_h"],
                "rho": round(rho, 3),
            },
            ensure_ascii=False,
        )
    )


def optimize_start(args) -> None:
    dist, elev, slope, lat_i, lon_i, bearings = read_gpx_resample(args.gpx, step_m=args.step_m)

    # Position moyenne pour météo
    lat = float(np.mean(lat_i))
    lon = float(np.mean(lon_i))

    # Récupère la série horaire à partir de maintenant (UTC)
    # On réutilise fetch_open_meteo pour chaque index horaire (0..23).
    hours = list(range(args.start_hour, args.end_hour + 1))
    results = []
    best = None

    for hr in hours:
        w = fetch_open_meteo(lat, lon, hour_utc_index=hr)
        airtemp = w["temperature_C"]
        humidity = w["humidity_frac"]
        pressure = w["pressure_Pa"]
        wind_u, wind_v = met_wdir_to_uv(w["wind_speed_mps"], w["wind_dir_deg"])
        # build env & rb
        rb, env, rho = _build_rb_env(args, airtemp, humidity, pressure, wind_u, wind_v)
        # pacing (même heuristique) et simulation
        P_target = pace_heuristic(
            dist,
            slope,
            bearings,
            rb,
            env,
            P_flat=args.power_flat,
            up_mult=args.up_mult,
            down_mult=args.down_mult,
            max_delta_w=args.max_delta,
        )
        _, _, T, _ = simulate(dist, slope, bearings, P_target, rb, env)
        results.append((hr, T, rho, w))

        if best is None or best[1] > T:
            best = (hr, T, rho, w, P_target)  # garde P_target pour export

    # best ne peut pas être None ici car hours contient au moins un élément
    assert best is not None, "Aucune heure n'a été testée"

    # Sauvegarde JSON + graphique
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "plots"), exist_ok=True)
    out = {
        "results": [
            {"hour": hr, "time_s": float(T), "time_h": float(T / 3600.0)} for hr, T, _, _ in results
        ],
        "best_hour": best[0],
        "best_time_s": float(best[1]),
        "best_time_h": float(best[1] / 3600.0),
    }
    with open(os.path.join(args.output_dir, "optimize_start.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    # Plot heure vs temps (h)
    import matplotlib.pyplot as plt

    hrs = [r[0] for r in results]
    th = [r[1] / 3600.0 for r in results]
    plt.figure()
    plt.plot(hrs, th, marker="o")
    plt.xlabel("Heure (index)")
    plt.ylabel("Temps estimé (h)")
    plt.title("Heure de départ vs Temps total estimé")
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, "plots", "optimize_start.png"))

    # Export GPX avec cibles pour l'heure optimale
    if args.export_gpx:
        # Re-simule à l'heure optimale pour garantir cohérence, et exporte GPX
        hr = best[0]
        w = best[3]
        airtemp = w["temperature_C"]
        humidity = w["humidity_frac"]
        pressure = w["pressure_Pa"]
        wind_u, wind_v = met_wdir_to_uv(w["wind_speed_mps"], w["wind_dir_deg"])
        rb, env, rho = _build_rb_env(args, airtemp, humidity, pressure, wind_u, wind_v)
        P_target = best[4]
        # On peut calculer v/dt aussi si besoin, mais pour le GPX seules lat/lon/ele/power suffisent
        gpx_out = os.path.join(args.output_dir, f"power_targets_best_hour_{hr}.gpx")
        write_power_gpx(gpx_out, lat_i, lon_i, elev, P_target, name=f"optiride-best-hour-{hr}")

    print(
        json.dumps(
            {"best_hour": best[0], "best_time_h": round(best[1] / 3600.0, 3)}, ensure_ascii=False
        )
    )


def main() -> None:
    p = argparse.ArgumentParser(
        prog="pace-gpx", description="Optimiseur de pacing vélo à partir d'un GPX"
    )
    sub = p.add_subparsers(dest="cmd")

    c = sub.add_parser("compute", help="Calculer la puissance cible et le plan de ravitaillement")
    # Required: trace et infos cycliste
    c.add_argument("--gpx", required=True, help="Chemin du fichier GPX")
    c.add_argument("--mass", type=float, required=True, help="Poids du cycliste (kg)")
    c.add_argument("--ftp", type=float, required=True, help="FTP du cycliste (W)")
    c.add_argument(
        "--height",
        type=float,
        default=None,
        help="Taille du cycliste (m) - ajuste automatiquement le CdA",
    )

    # Configuration vélo depuis bibliothèque (recommandé)
    c.add_argument(
        "--bike-type",
        type=str,
        default="aero_road",
        choices=list_bike_types(),
        help="Type de vélo (défaut: aero_road)",
    )
    c.add_argument(
        "--position",
        type=str,
        default="drops",
        choices=list_positions(),
        help="Position sur le vélo (défaut: drops)",
    )
    c.add_argument(
        "--wheels",
        type=str,
        default=None,
        help="Type de roues (défaut: mid_depth)",
    )

    # Configuration manuelle avancée (optionnel, surcharge --bike-type)
    c.add_argument("--bike-mass", type=float, default=None, help="Poids vélo manuel (kg)")
    c.add_argument("--cda", type=float, default=None, help="CdA manuel (m²)")
    c.add_argument("--crr", type=float, default=None, help="Crr manuel")
    c.add_argument("--eff", type=float, default=None, help="Rendement transmission manuel")

    # Paramètres de performance optionnels
    c.add_argument("--cp", type=float, default=None, help="Critical Power (W)")
    c.add_argument("--wprime", type=float, default=None, help="W' (J)")
    c.add_argument("--age", type=int, default=None, help="Âge (ans)")
    # Weather controls
    c.add_argument(
        "--auto-weather",
        action="store_true",
        help="Récupère automatiquement la météo via Open-Meteo",
    )
    c.add_argument(
        "--hour",
        type=int,
        default=None,
        help="Heure de départ (index simplifié 0..n) pour choisir la tranche horaire météo",
    )
    c.add_argument(
        "--airtemp", type=float, default=15.0, help="Température (°C) si pas d'auto-weather"
    )
    c.add_argument(
        "--pressure", type=float, default=101325.0, help="Pression (Pa) si pas d'auto-weather"
    )
    c.add_argument(
        "--humidity", type=float, default=0.5, help="Humidité relative 0..1 si pas d'auto-weather"
    )
    c.add_argument(
        "--wind-u",
        dest="wind_u",
        type=float,
        default=0.0,
        help="Vent u Est (m/s) si pas d'auto-weather",
    )
    c.add_argument(
        "--wind-v",
        dest="wind_v",
        type=float,
        default=0.0,
        help="Vent v Nord (m/s) si pas d'auto-weather",
    )
    # Pacing config
    c.add_argument("--power-flat", type=float, required=True, help="Puissance de base sur plat (W)")
    c.add_argument("--up-mult", type=float, default=1.10, help="Multiplicateur en montée")
    c.add_argument("--down-mult", type=float, default=0.75, help="Multiplicateur en descente")
    c.add_argument("--max-delta", type=float, default=30.0, help="Variation max entre pas (W)")
    c.add_argument("--step-m", type=float, default=20.0, help="Pas de rééchantillonnage (m)")
    c.add_argument(
        "--gross-eff", type=float, default=0.22, help="Rendement global (mécanique -> alimentaire)"
    )
    c.add_argument("--output-dir", default="outputs", help="Dossier de sortie")
    # Exports
    c.add_argument(
        "--export-gpx", action="store_true", help="Exporte une trace GPX avec les puissances cibles"
    )
    c.add_argument(
        "--start-time-now",
        action="store_true",
        help="Ajoute des timestamps depuis maintenant dans la GPX exportée",
    )
    c.set_defaults(func=compute)

    o = sub.add_parser(
        "optimize-start",
        help="Balaye les heures et choisit l'heure de départ optimale (météo/vent)",
    )
    # Required: trace et infos cycliste
    o.add_argument("--gpx", required=True, help="Chemin du fichier GPX")
    o.add_argument("--mass", type=float, required=True, help="Poids du cycliste (kg)")
    o.add_argument("--ftp", type=float, required=True, help="FTP du cycliste (W)")
    o.add_argument(
        "--height",
        type=float,
        default=None,
        help="Taille du cycliste (m) - ajuste automatiquement le CdA",
    )

    # Configuration vélo depuis bibliothèque (recommandé)
    o.add_argument(
        "--bike-type",
        type=str,
        default="aero_road",
        choices=list_bike_types(),
        help="Type de vélo (défaut: aero_road)",
    )
    o.add_argument(
        "--position",
        type=str,
        default="drops",
        choices=list_positions(),
        help="Position sur le vélo (défaut: drops)",
    )
    o.add_argument(
        "--wheels",
        type=str,
        default=None,
        help="Type de roues (défaut: mid_depth)",
    )

    # Configuration manuelle avancée (optionnel, surcharge --bike-type)
    o.add_argument("--bike-mass", type=float, default=None, help="Poids vélo manuel (kg)")
    o.add_argument("--cda", type=float, default=None, help="CdA manuel (m²)")
    o.add_argument("--crr", type=float, default=None, help="Crr manuel")
    o.add_argument("--eff", type=float, default=None, help="Rendement transmission manuel")

    # Paramètres de performance optionnels
    o.add_argument("--cp", type=float, default=None, help="Critical Power (W)")
    o.add_argument("--wprime", type=float, default=None, help="W' (J)")
    o.add_argument("--age", type=int, default=None, help="Âge (ans)")
    # Pacing config
    o.add_argument("--power-flat", type=float, required=True, help="Puissance de base sur plat (W)")
    o.add_argument("--up-mult", type=float, default=1.10, help="Multiplicateur en montée")
    o.add_argument("--down-mult", type=float, default=0.75, help="Multiplicateur en descente")
    o.add_argument("--max-delta", type=float, default=30.0, help="Variation max entre pas (W)")
    o.add_argument("--step-m", type=float, default=20.0, help="Pas de rééchantillonnage (m)")
    o.add_argument(
        "--gross-eff", type=float, default=0.22, help="Rendement global (mécanique -> alimentaire)"
    )
    o.add_argument("--output-dir", default="outputs", help="Dossier de sortie")
    # Balayage horaire
    o.add_argument(
        "--start-hour",
        type=int,
        default=6,
        help="Heure de départ minimale (index horaire UTC simplifié)",
    )
    o.add_argument(
        "--end-hour",
        type=int,
        default=20,
        help="Heure de départ maximale (index horaire UTC simplifié)",
    )
    # Export GPX de la meilleure heure
    o.add_argument(
        "--export-gpx",
        action="store_true",
        help="Exporte la GPX avec puissances cibles pour l'heure optimale",
    )
    o.set_defaults(func=optimize_start)

    args = p.parse_args()
    if args.cmd is None:
        p.print_help()
        return
    args.func(args)
