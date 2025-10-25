"""Interactive map export using Folium.

Creates HTML maps with power zones, elevation profile, and ride statistics.
"""

from typing import Optional

import numpy as np

from optiride.fueling import FuelingPoint, calculate_power_zones


def export_interactive_map(
    output_path: str,
    lats: np.ndarray,
    lons: np.ndarray,
    elevations: np.ndarray,
    powers: np.ndarray,
    distances_km: np.ndarray,
    speeds_kmh: np.ndarray,
    ftp: float,
    title: str = "OptiRide - Pacing Strategy",
    summary_stats: Optional[dict] = None,
    fueling_points: Optional[list[FuelingPoint]] = None,
) -> None:
    """Export an interactive HTML map with power zones and elevation profile.

    Args:
        output_path: Path to save the HTML file.
        lats: Latitude coordinates (degrees).
        lons: Longitude coordinates (degrees).
        elevations: Elevation values (meters).
        powers: Power target values (watts).
        distances_km: Cumulative distance (kilometers).
        speeds_kmh: Speed values (km/h).
        ftp: Functional Threshold Power (watts) for personalized zones.
        title: Map title.
        summary_stats: Optional dict with ride summary (time, kcal, etc.).
        fueling_points: Optional list of FuelingPoint objects to display on map.

    Example:
        >>> export_interactive_map(
        ...     "ride_map.html",
        ...     lats=np.array([45.0, 45.1]),
        ...     lons=np.array([6.0, 6.1]),
        ...     elevations=np.array([500, 600]),
        ...     powers=np.array([200, 250]),
        ...     distances_km=np.array([0.0, 5.0]),
        ...     speeds_kmh=np.array([30.0, 25.0]),
        ...     ftp=260.0,
        ... )
    """
    try:
        import folium
        from folium import plugins
    except ImportError as e:
        raise ImportError(
            "folium est requis pour l'export de cartes interactives. "
            "Installez-le avec: pip install folium"
        ) from e

    # Center map on route midpoint
    center_lat = float(np.mean(lats))
    center_lon = float(np.mean(lons))

    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="OpenStreetMap",
    )

    # Add alternative tile layers
    folium.TileLayer(
        tiles="https://tile.opentopomap.org/{z}/{x}/{y}.png",
        attr='Map data: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
        name="Terrain",
        max_zoom=17,
    ).add_to(m)
    folium.TileLayer(
        tiles="CartoDB positron",
        name="Light",
    ).add_to(m)

    # Calculate personalized power zones based on FTP
    zones = calculate_power_zones(ftp)

    # Define power zones colors
    def get_power_color(power: float) -> str:
        """Get color based on power value using personalized FTP zones."""
        if power < zones["endurance"][0]:
            return "#4CAF50"  # Green - Recovery
        elif power < zones["tempo"][0]:
            return "#8BC34A"  # Light green - Endurance
        elif power < zones["threshold"][0]:
            return "#FFEB3B"  # Yellow - Tempo
        elif power < zones["vo2max"][0]:
            return "#FF9800"  # Orange - Threshold
        elif power < zones["anaerobic"][0]:
            return "#FF5722"  # Deep orange - VO2max
        else:
            return "#F44336"  # Red - Anaerobic

    # Create segments for colored polyline
    points = list(zip(lats, lons, powers, elevations, distances_km, speeds_kmh))

    # Add colored route segments
    for i in range(len(points) - 1):
        lat1, lon1, p1, elev1, dist1, spd1 = points[i]
        lat2, lon2, p2, elev2, _dist2, spd2 = points[i + 1]

        # Use average power for segment color
        avg_power = (p1 + p2) / 2
        color = get_power_color(avg_power)

        # Create popup with segment info
        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>Segment {i + 1}</b><br>
            Distance: {dist1:.1f} km<br>
            Power: {avg_power:.0f} W<br>
            Speed: {(spd1 + spd2) / 2:.1f} km/h<br>
            Elevation: {(elev1 + elev2) / 2:.0f} m
        </div>
        """

        folium.PolyLine(
            locations=[[lat1, lon1], [lat2, lon2]],
            color=color,
            weight=5,
            opacity=0.8,
            popup=folium.Popup(popup_html, max_width=200),
        ).add_to(m)

    # Add start marker
    folium.Marker(
        location=[float(lats[0]), float(lons[0])],
        popup="Départ",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)

    # Add finish marker
    folium.Marker(
        location=[float(lats[-1]), float(lons[-1])],
        popup="Arrivée",
        icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
    ).add_to(m)

    # Add fueling point markers
    if fueling_points:
        for fp in fueling_points:
            # Find closest GPS coordinates for this fueling point
            idx = np.argmin(np.abs(distances_km - fp.distance_km))
            fuel_lat = float(lats[idx])
            fuel_lon = float(lons[idx])

            # Determine marker color based on fatigue
            if fp.fatigue_index > 70:
                marker_color = "red"
                fatigue_icon = "⚠️"
            elif fp.fatigue_index > 50:
                marker_color = "orange"
                fatigue_icon = "⚡"
            else:
                marker_color = "blue"
                fatigue_icon = "💪"

            # Create detailed popup
            popup_html = f"""
            <div style="font-family: Arial; font-size: 13px; min-width: 250px;">
                <h4 style="margin-top: 0; color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 5px;">
                    🍎 Ravitaillement #{fueling_points.index(fp) + 1}
                </h4>
                <table style="width: 100%; font-size: 12px;">
                    <tr><td><b>Distance:</b></td><td>{fp.distance_km:.1f} km</td></tr>
                    <tr><td><b>Temps:</b></td><td>{fp.time_h * 60:.0f} min</td></tr>
                    <tr><td><b>Type:</b></td><td><b>{fp.refuel_type.upper()}</b></td></tr>
                    <tr><td colspan="2" style="border-top: 1px solid #ccc; padding-top: 5px;"><b>Nutrition:</b></td></tr>
                    <tr><td>• Glucides:</td><td>{fp.carbs_g:.0f} g</td></tr>
                    <tr><td>• Liquides:</td><td>{fp.fluids_ml:.0f} ml</td></tr>
                    <tr><td>• Sodium:</td><td>{fp.sodium_mg:.0f} mg</td></tr>
                    <tr><td colspan="2" style="border-top: 1px solid #ccc; padding-top: 5px;"><b>État physique:</b></td></tr>
                    <tr><td>• Fatigue:</td><td>{fp.fatigue_index:.0f}% {fatigue_icon}</td></tr>
                    <tr><td>• W' restant:</td><td>{fp.w_prime_balance_pct * 100:.0f}%</td></tr>
                    <tr><td>• Déficit:</td><td>{fp.energy_deficit_kcal:.0f} kcal</td></tr>
                </table>
                <div style="margin-top: 8px; padding: 8px; background-color: #f5f5f5; border-radius: 4px; font-size: 11px;">
                    <b>💡 Recommandations:</b><br>
                    {fp.notes}
                </div>
            </div>
            """

            folium.Marker(
                location=[fuel_lat, fuel_lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=marker_color, icon="cutlery", prefix="fa"),
            ).add_to(m)

    # Add summary stats box
    if summary_stats:
        stats_html = f"""
        <div style="position: fixed;
                    top: 10px;
                    right: 10px;
                    width: 280px;
                    background-color: white;
                    border: 2px solid #1976d2;
                    border-radius: 8px;
                    padding: 15px;
                    font-family: Arial;
                    z-index: 1000;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
            <h3 style="margin-top: 0; color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 8px;">
                📊 {title}
            </h3>
            <table style="width: 100%; font-size: 13px;">
                <tr><td><b>Distance:</b></td><td>{summary_stats.get("distance_km", 0):.1f} km</td></tr>
                <tr><td><b>Temps estimé:</b></td><td>{summary_stats.get("time_h", 0):.2f} h</td></tr>
                <tr><td><b>Dénivelé:</b></td><td>{summary_stats.get("elevation_gain", 0):.0f} m</td></tr>
                <tr><td><b>Puissance moy:</b></td><td>{summary_stats.get("avg_power", 0):.0f} W</td></tr>
                <tr><td><b>Vitesse moy:</b></td><td>{summary_stats.get("avg_speed", 0):.1f} km/h</td></tr>
                <tr><td><b>Calories:</b></td><td>{summary_stats.get("kcal", 0):.0f} kcal</td></tr>
            </table>
        </div>
        """
        m.get_root().html.add_child(folium.Element(stats_html))  # type: ignore[attr-defined]

    # Add power zones legend with personalized FTP values
    legend_html = f"""
    <div style="position: fixed;
                bottom: 50px;
                left: 10px;
                background-color: white;
                border: 2px solid #1976d2;
                border-radius: 8px;
                padding: 12px;
                font-family: Arial;
                font-size: 12px;
                z-index: 1000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
        <b style="color: #1976d2; font-size: 13px;">⚡ Zones de puissance (FTP: {ftp:.0f}W)</b><br>
        <div style="margin-top: 8px;">
            <span style="color: #4CAF50; font-size: 20px;">●</span> &lt;{zones["endurance"][0]:.0f}W Récupération<br>
            <span style="color: #8BC34A; font-size: 20px;">●</span> {zones["endurance"][0]:.0f}-{zones["tempo"][0]:.0f}W Endurance<br>
            <span style="color: #FFEB3B; font-size: 20px;">●</span> {zones["tempo"][0]:.0f}-{zones["threshold"][0]:.0f}W Tempo<br>
            <span style="color: #FF9800; font-size: 20px;">●</span> {zones["threshold"][0]:.0f}-{zones["vo2max"][0]:.0f}W Seuil<br>
            <span style="color: #FF5722; font-size: 20px;">●</span> {zones["vo2max"][0]:.0f}-{zones["anaerobic"][0]:.0f}W VO2max<br>
            <span style="color: #F44336; font-size: 20px;">●</span> &gt;{zones["anaerobic"][0]:.0f}W Anaérobie
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))  # type: ignore[attr-defined]

    # Add elevation profile chart (using MiniMap-like approach)
    # Create a simple elevation chart as HTML/SVG
    elev_min, elev_max = float(np.min(elevations)), float(np.max(elevations))
    elev_range = elev_max - elev_min if elev_max > elev_min else 100

    # Sample points for elevation profile (max 100 points for performance)
    step = max(1, len(elevations) // 100)
    profile_indices = list(range(0, len(elevations), step))

    profile_html = (
        '<div style="position: fixed; bottom: 50px; right: 10px; width: 400px; height: '
        "120px; background-color: white; border: 2px solid #1976d2; border-radius: "
        "8px; padding: 10px; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,"
        '0.2);"><b style="color: #1976d2;">📈 Profil altimétrique</b><br><svg '
        'width="380" height="80" style="margin-top: 5px;">'
    )

    # Draw elevation profile
    for profile_i in profile_indices:
        x = float((profile_i / len(elevations)) * 380)
        y = float(80 - ((elevations[profile_i] - elev_min) / elev_range) * 70)
        profile_html += f'<circle cx="{x}" cy="{y}" r="1.5" fill="#1976d2" opacity="0.6"/>'

    # Add baseline
    profile_html += '<line x1="0" y1="80" x2="380" y2="80" stroke="#ccc" stroke-width="1"/>'
    profile_html += f'<text x="5" y="15" font-size="10" fill="#666">{elev_max:.0f}m</text>'
    profile_html += f'<text x="5" y="75" font-size="10" fill="#666">{elev_min:.0f}m</text>'
    profile_html += "</svg></div>"

    m.get_root().html.add_child(folium.Element(profile_html))  # type: ignore[attr-defined]

    # Add fullscreen control
    plugins.Fullscreen().add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save map
    m.save(output_path)
