import datetime
from collections.abc import Iterable
from typing import Optional


def write_power_gpx(
    path: str,
    lats: Iterable[float],
    lons: Iterable[float],
    elevs: Iterable[float],
    powers_W: Iterable[float],
    name: str = "optiride-power-targets",
    start_time: Optional[datetime.datetime] = None,
):
    """Écrit une trace GPX avec un tag d'extension par point contenant la puissance cible (W).
    Si start_time est fourni, les timestamps seront incrémentés par les échantillons
    (1s par point approx.).
    """
    # NB: on n'impose pas la balise GPX d'extensions officielles; on ajoute une extension
    # personnalisée <optiride:power>.
    # Les logiciels qui lisent des extensions custom pourront l'exploiter; sinon, au moins la
    # géométrie est visible.
    it = list(zip(lats, lons, elevs, powers_W))
    t0 = start_time
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(
        '<gpx creator="optiride" version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:optiride="https://example.com/optiride">'
    )
    lines.append(f"  <trk><name>{name}</name><trkseg>")
    for i, (lat, lon, ele, p) in enumerate(it):
        lines.append(f'    <trkpt lat="{lat:.6f}" lon="{lon:.6f}">')
        lines.append(f"      <ele>{float(ele):.1f}</ele>")
        if t0 is not None:
            ti = t0 + datetime.timedelta(seconds=i)
            lines.append(f"      <time>{ti.replace(microsecond=0).isoformat()}Z</time>")
        lines.append("      <extensions>")
        lines.append(f"        <optiride:target_watts>{float(p):.1f}</optiride:target_watts>")
        lines.append("      </extensions>")
        lines.append("    </trkpt>")
    lines.append("  </trkseg></trk>")
    lines.append("</gpx>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
