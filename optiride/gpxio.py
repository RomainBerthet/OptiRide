import gpxpy
import numpy as np

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    dphi = np.radians(lat2-lat1)
    dl = np.radians(lon2-lon1)
    a = np.sin(dphi/2.0)**2 + np.cos(np.radians(lat1))*np.cos(np.radians(lat2))*np.sin(dl/2.0)**2
    return 2*R*np.arcsin(np.sqrt(a))

def _bearing_deg(lat1, lon1, lat2, lon2):
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dlon = np.radians(lon2 - lon1)
    y = np.sin(dlon) * np.cos(phi2)
    x = np.cos(phi1)*np.sin(phi2) - np.sin(phi1)*np.cos(phi2)*np.cos(dlon)
    brng = np.degrees(np.arctan2(y, x))
    return (brng + 360) % 360

def read_gpx_resample(path: str, step_m: float = 20.0):
    with open(path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)
    pts = []
    for trk in gpx.tracks:
        for seg in trk.segments:
            for p in seg.points:
                pts.append((p.latitude, p.longitude, p.elevation))
    if len(pts) < 2:
        raise ValueError("GPX trop court.")
    pts = np.array(pts, dtype=float)
    lats = pts[:,0]; lons = pts[:,1]; elev = pts[:,2]

    # Distance cumulée sur points initiaux
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + _haversine(lats[i-1], lons[i-1], lats[i], lons[i]))
    d = np.array(d)

    # Rééchantillonnage
    dist_grid = np.arange(0, d[-1], step_m)
    lat_i = np.interp(dist_grid, d, lats)
    lon_i = np.interp(dist_grid, d, lons)
    elev_i = np.interp(dist_grid, d, elev)

    # Pente locale
    slope = np.gradient(elev_i, dist_grid, edge_order=2)

    # Cap (bearing) entre points rééchantillonnés
    bearings = np.zeros_like(dist_grid)
    for i in range(1, len(dist_grid)):
        bearings[i] = _bearing_deg(lat_i[i-1], lon_i[i-1], lat_i[i], lon_i[i])
    bearings[0] = bearings[1]

    return dist_grid, elev_i, slope, lat_i, lon_i, bearings
