"""Rugosité z0 autour de la cheminée, à la manière d'AERSURFACE (moyenne géométrique pondérée par 1/distance,
rayon 1 km, 12 secteurs de 30°), à partir de Corine Land Cover 2018.

Valeurs d'hiver par classe : approximations reprises des tables AERSURFACE (classes NLCD les plus proches),
données à titre d'ordre de grandeur ; l'incertitude sur ces valeurs est du même ordre que l'écart entre classes.
"""
import json
from pathlib import Path

import numpy as np
from shapely import contains_xy
from shapely.geometry import shape

PROJET = Path(__file__).resolve().parent.parent
X0, Y0 = 576601.2, 5453845.2
Z0_HIVER = {"111": 1.0, "112": 0.4, "121": 0.8, "122": 0.1, "124": 0.1, "133": 0.1, "141": 0.05, "142": 0.05,
            "211": 0.01, "221": 0.1, "231": 0.01, "242": 0.05, "311": 0.5, "324": 0.15}

if __name__ == "__main__":
    pas = 10.0
    x, y = np.meshgrid(np.arange(X0 - 1000, X0 + 1000 + pas, pas), np.arange(Y0 - 1000, Y0 + 1000 + pas, pas))
    r = np.hypot(x - X0, y - Y0)
    m = (r <= 1000) & (r > 0)
    x, y, r = x[m], y[m], r[m]
    z0 = np.full(x.shape, np.nan)
    for e in json.loads((PROJET / "donnees/occupation_sol/clc18.json").read_text())["features"]:
        code = e["properties"]["code_18"]
        dedans = contains_xy(shape(e["geometry"]), x, y)
        z0[dedans] = Z0_HIVER.get(code, np.nan)
    ok = np.isfinite(z0)
    print(f"points couverts : {ok.mean():.1%}")
    w = 1 / r
    def moy(sel):
        return float(np.exp(np.sum(w[sel] * np.log(z0[sel])) / np.sum(w[sel])))
    print(f"z0 global (1 km, pondéré 1/r) : {moy(ok):.2f} m")
    az = (np.degrees(np.arctan2(x - X0, y - Y0)) + 360) % 360
    for s in range(12):
        sel = ok & (az >= 30 * s) & (az < 30 * (s + 1))
        print(f"  secteur {30 * s:3d}–{30 * (s + 1):3d}° : z0 = {moy(sel):.2f} m")
