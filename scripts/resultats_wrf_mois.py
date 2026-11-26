"""Étape 8 — tableau des contributions de l'usine (NOx, µg/m³) pour les calculs mensuels aermod/{jan,jul}_*/.

Pour chaque dossier : maximum de la moyenne du mois sur la grille (distance et azimut depuis la cheminée), maximum
horaire sur la grille, moyenne du mois aux trois stations (Jean d'Aulan, Doumer, Bétheny, dans l'ordre de
stations.rou). Usage : resultats_wrf_mois.py jan|jul
"""
import sys

import numpy as np

from aermod_wrf_janvier import PROJET

X0, Y0 = 576601.2, 5453845.2


def lire_plt(f):
    return np.array([[float(v) for v in l.split()[:3]] for l in f.open() if not l.startswith("*")])


def ou(x, y):
    d = np.hypot(x - X0, y - Y0) / 1000
    az = np.degrees(np.arctan2(x - X0, y - Y0)) % 360
    return f"{d:.1f} km, {az:.0f}°"


if __name__ == "__main__":
    mois = sys.argv[1]
    print(f"| Cas | max moyenne du mois (lieu) | max 1 h (lieu) | Jean d'Aulan / Doumer / Bétheny |")
    print("|---|---|---|---|")
    for d in sorted((PROJET / "aermod").glob(f"{mois}_*")):
        if not (d / "periode_grille.plt").exists():
            continue
        p = lire_plt(d / "periode_grille.plt"); h = lire_plt(d / "max1h_grille.plt")
        s = lire_plt(d / "periode_stations.plt")[:, 2]
        i, j = p[:, 2].argmax(), h[:, 2].argmax()
        print(f"| {d.name.removeprefix(mois + '_')} | {p[i, 2]:.2f} ({ou(*p[i, :2])}) | {h[j, 2]:.1f} ({ou(*h[j, :2])}) | "
              + " / ".join(f"{v:.3f}" for v in s) + " |")
