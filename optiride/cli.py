import argparse
import datetime
import json
import os
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .bike_library import get_bike_config, list_bike_types, list_positions, list_wheel_types
from .env import air_density_kg_m3
from .exporter import write_power_gpx
from .fueling import calculate_fueling_points
from .gpxio import read_gpx_resample
from .map_exporter import export_interactive_map
from .models import Environment, RiderBike
from .nutrition import fueling_plan
from .optimizer import pace_heuristic, simulate
from .weather import fetch_open_meteo, met_wdir_to_uv


def _calculate_target_power(args, estimated_duration_h: Optional[float] = None) -> float:
    """Calculate target power from FTP, intensity factor, or power-flat.

    Priority order:
    1. --power-flat (explicit power)
    2. --intensity-factor (fraction of FTP)
    3. Auto-calculate from FTP based on estimated duration

    Args:
        args: Parsed command-line arguments.
        estimated_duration_h: Estimated ride duration in hours (optional).

    Returns:
        Target power in watts.
    """
    # Priority 1: Explicit power-flat
    if args.power_flat is not None:
        return args.power_flat

    # Check FTP is available
    if args.ftp is None:
        raise ValueError(
            "FTP est requis pour calculer automatiquement la puissance cible. "
            "Spécifiez --ftp ou utilisez --power-flat explicitement."
        )

    # Priority 2: Intensity factor
    if args.intensity_factor is not None:
        if not 0.0 < args.intensity_factor <= 1.0:
            raise ValueError("--intensity-factor doit être entre 0.0 et 1.0")
        return args.ftp * args.intensity_factor

    # Priority 3: Auto-calculate based on duration
    # Use conservative defaults based on typical endurance rides
    if estimated_duration_h is not None:
        if estimated_duration_h < 1.0:
            # Short effort: 90-95% FTP
            intensity = 0.92
        elif estimated_duration_h < 2.0:
            # Medium effort: 85-90% FTP
            intensity = 0.87
        elif estimated_duration_h < 4.0:
            # Long effort: 75-85% FTP
            intensity = 0.80
        else:
            # Very long effort: 65-75% FTP
            intensity = 0.70
    else:
        # No duration estimate: use conservative 75% FTP (tempo pace)
        intensity = 0.75

    power = args.ftp * intensity
    print(f"💡 Puissance cible calculée automatiquement: {power:.0f}W ({intensity * 100:.0f}% FTP)")
    return power


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

    # Calculate target power (auto-calculated if not specified)
    power_flat = _calculate_target_power(args, estimated_duration_h=None)

    P_target = pace_heuristic(
        dist,
        slope,
        bearings,
        rb,
        env,
        P_flat=power_flat,
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

    # Export carte interactive si demandé
    if args.export_map:
        map_out = os.path.join(args.output_dir, "interactive_map.html")
        # Calculate elevation gain
        elevation_gain = float(np.sum(np.maximum(0, np.diff(elev))))
        summary_stats = {
            "distance_km": float(dist[-1] / 1000.0),
            "time_h": float(T / 3600.0),
            "elevation_gain": elevation_gain,
            "avg_power": float(np.mean(P_target)),
            "avg_speed": float(np.mean(v) * 3.6),
            "kcal": float(fuel["kcal"]),
        }

        # Calculate fueling points based on ride data
        fueling_points = calculate_fueling_points(
            distances_km=df["dist_m"].values / 1000.0,
            times_h=df["t_cum_s"].values / 3600.0,
            powers_w=df["P_target_W"].values,
            ftp=rb.ftp if rb.ftp is not None else args.ftp,
            cp=rb.cp,
            w_prime=rb.w_prime_j,
            refuel_interval_min=20.0,
            carbs_per_hour=60.0,
        )

        export_interactive_map(
            map_out,
            lats=df["lat"].values,
            lons=df["lon"].values,
            elevations=df["elev_m"].values,
            powers=df["P_target_W"].values,
            distances_km=df["dist_m"].values / 1000.0,
            speeds_kmh=df["v_ms"].values * 3.6,
            ftp=rb.ftp if rb.ftp is not None else args.ftp,
            title="OptiRide - Stratégie de pacing",
            summary_stats=summary_stats,
            fueling_points=fueling_points,
        )
        print(f"Carte interactive exportée: {map_out}")
        print(f"Points de ravitaillement: {len(fueling_points)}")

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

    # Calculate target power once (same for all hours)
    power_flat = _calculate_target_power(args, estimated_duration_h=None)

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
            P_flat=power_flat,
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

    # Export carte interactive si demandé
    if args.export_map:
        # Re-simulate for the best hour to get complete data
        hr = best[0]
        w = best[3]
        airtemp = w["temperature_C"]
        humidity = w["humidity_frac"]
        pressure = w["pressure_Pa"]
        wind_u, wind_v = met_wdir_to_uv(w["wind_speed_mps"], w["wind_dir_deg"])
        rb, env, rho = _build_rb_env(args, airtemp, humidity, pressure, wind_u, wind_v)
        P_target = best[4]
        v, dt, T, W = simulate(dist, slope, bearings, P_target, rb, env)

        # Create DataFrame for calculations
        times_cum_s = np.cumsum(dt)
        distances_km = dist / 1000.0

        # Calculate fueling points
        fueling_points = calculate_fueling_points(
            distances_km=distances_km,
            times_h=times_cum_s / 3600.0,
            powers_w=P_target,
            ftp=rb.ftp if rb.ftp is not None else args.ftp,
            cp=rb.cp,
            w_prime=rb.w_prime_j,
            refuel_interval_min=20.0,
            carbs_per_hour=60.0,
        )

        # Calculate stats
        elevation_gain = float(np.sum(np.maximum(0, np.diff(elev))))
        fuel = fueling_plan(T, W, gross_eff=args.gross_eff)
        summary_stats = {
            "distance_km": float(dist[-1] / 1000.0),
            "time_h": float(T / 3600.0),
            "elevation_gain": elevation_gain,
            "avg_power": float(np.mean(P_target)),
            "avg_speed": float(np.mean(v) * 3.6),
            "kcal": float(fuel["kcal"]),
        }

        map_out = os.path.join(args.output_dir, f"interactive_map_best_hour_{hr}.html")
        export_interactive_map(
            map_out,
            lats=lat_i,
            lons=lon_i,
            elevations=elev,
            powers=P_target,
            distances_km=distances_km,
            speeds_kmh=v * 3.6,
            ftp=rb.ftp if rb.ftp is not None else args.ftp,
            title=f"OptiRide - Heure optimale: {hr}h",
            summary_stats=summary_stats,
            fueling_points=fueling_points,
        )
        print(f"Carte interactive exportée: {map_out}")
        print(f"Points de ravitaillement: {len(fueling_points)}")

    print(
        json.dumps(
            {"best_hour": best[0], "best_time_h": round(best[1] / 3600.0, 3)}, ensure_ascii=False
        )
    )


def _add_rider_args(parser):
    """Add common rider and bike arguments to a parser."""
    # Required: trace et infos cycliste
    parser.add_argument("--gpx", required=True, help="Chemin du fichier GPX")
    parser.add_argument("--mass", type=float, required=True, help="Poids du cycliste (kg)")
    parser.add_argument("--ftp", type=float, required=True, help="FTP du cycliste (W)")
    parser.add_argument(
        "--height",
        type=float,
        default=None,
        help="Taille du cycliste (m) - ajuste automatiquement le CdA",
    )

    # Configuration vélo depuis bibliothèque (recommandé)
    parser.add_argument(
        "--bike-type",
        type=str,
        default="aero_road",
        choices=list_bike_types(),
        help="Type de vélo (défaut: aero_road)",
    )
    parser.add_argument(
        "--position",
        type=str,
        default="drops",
        choices=list_positions(),
        help="Position sur le vélo (défaut: drops)",
    )
    parser.add_argument(
        "--wheels",
        type=str,
        default=None,
        choices=list_wheel_types(),
        help="Type de roues (défaut: mid_depth)",
    )

    # Configuration manuelle avancée (optionnel, surcharge --bike-type)
    parser.add_argument("--bike-mass", type=float, default=None, help="Poids vélo manuel (kg)")
    parser.add_argument("--cda", type=float, default=None, help="CdA manuel (m²)")
    parser.add_argument("--crr", type=float, default=None, help="Crr manuel")
    parser.add_argument("--eff", type=float, default=None, help="Rendement transmission manuel")

    # Paramètres de performance optionnels
    parser.add_argument("--cp", type=float, default=None, help="Critical Power (W)")
    parser.add_argument("--wprime", type=float, default=None, help="W' (J)")
    parser.add_argument("--age", type=int, default=None, help="Âge (ans)")


def _add_pacing_args(parser):
    """Add common pacing strategy arguments to a parser."""
    parser.add_argument(
        "--power-flat",
        type=float,
        default=None,
        help="Puissance de base sur plat (W). Si non spécifié, calculé automatiquement depuis FTP",
    )
    parser.add_argument(
        "--intensity-factor",
        type=float,
        default=None,
        help="Facteur d'intensité (0.0-1.0, fraction du FTP). Alternative à --power-flat",
    )
    parser.add_argument("--up-mult", type=float, default=1.10, help="Multiplicateur en montée")
    parser.add_argument("--down-mult", type=float, default=0.75, help="Multiplicateur en descente")
    parser.add_argument("--max-delta", type=float, default=30.0, help="Variation max entre pas (W)")
    parser.add_argument("--step-m", type=float, default=20.0, help="Pas de rééchantillonnage (m)")
    parser.add_argument(
        "--gross-eff", type=float, default=0.22, help="Rendement global (mécanique -> alimentaire)"
    )
    parser.add_argument("--output-dir", default="outputs", help="Dossier de sortie")


def main() -> None:
    p = argparse.ArgumentParser(
        prog="pace-gpx", description="Optimiseur de pacing vélo à partir d'un GPX"
    )
    sub = p.add_subparsers(dest="cmd")

    c = sub.add_parser("compute", help="Calculer la puissance cible et le plan de ravitaillement")
    _add_rider_args(c)
    _add_pacing_args(c)

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

    # Exports
    c.add_argument(
        "--export-gpx", action="store_true", help="Exporte une trace GPX avec les puissances cibles"
    )
    c.add_argument("--export-map", action="store_true", help="Exporte une carte interactive HTML")
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
    _add_rider_args(o)
    _add_pacing_args(o)

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
    o.add_argument("--export-map", action="store_true", help="Exporte une carte interactive HTML")
    o.set_defaults(func=optimize_start)

    args = p.parse_args()
    if args.cmd is None:
        p.print_help()
        return
    args.func(args)
