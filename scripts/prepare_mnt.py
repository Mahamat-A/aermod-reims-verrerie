"""Télécharge le modèle numérique de terrain IGN et l'écrit en GeoTIFF UTM 31N pour AERMAP.

Source : Géoplateforme IGN, service WMS-R, couche ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES
(RGE ALTI, terrain nu : sans bâtiments ni arbres, contrairement à un modèle de surface).
Carré de 30 km centré sur la cheminée A, pas de 25 m.
"""

from pathlib import Path

import numpy as np
import requests
import tifffile

PROJET = Path(__file__).resolve().parent.parent
SORTIE = PROJET / "donnees" / "relief" / "mnt_ign_25m_utm31n.tif"
CHEMINEE_A = (576601.2, 5453845.2)   # UTM 31N, donnees/installation.md
DEMI_COTE = 15000.0                  # m
PAS = 25.0                           # m
WMS = "https://data.geopf.fr/wms-r"
COUCHE = "ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES"


def telecharger(x0, y0, x1, y1, n):
    """Altitudes en float32, n × n, ligne 0 au nord (format BIL brut du WMS)."""
    parametres = {
        "SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetMap", "LAYERS": COUCHE,
        "STYLES": "", "CRS": "EPSG:32631", "BBOX": f"{x0},{y0},{x1},{y1}",
        "WIDTH": n, "HEIGHT": n, "FORMAT": "image/x-bil;bits=32",
    }
    reponse = requests.get(WMS, params=parametres, timeout=300)
    reponse.raise_for_status()
    altitudes = np.frombuffer(reponse.content, dtype="<f4")
    if altitudes.size != n * n:
        raise ValueError(f"Réponse inattendue du WMS ({len(reponse.content)} octets).")
    return altitudes.reshape(n, n)


def ecrire_geotiff(chemin, altitudes, x_ouest, y_nord, pas):
    """GeoTIFF projeté UTM 31N / WGS84 (EPSG:32631), pixel = surface, mètres."""
    geocles = [
        1, 1, 0, 5,
        1024, 0, 1, 1,       # GTModelType : projeté
        1025, 0, 1, 1,       # GTRasterType : PixelIsArea
        3072, 0, 1, 32631,   # ProjectedCSType : WGS 84 / UTM 31N
        3076, 0, 1, 9001,    # unités horizontales : mètre
        4099, 0, 1, 9001,    # unités verticales : mètre
    ]
    etiquettes = [
        (33550, "d", 3, (pas, pas, 0.0), False),                          # ModelPixelScale
        (33922, "d", 6, (0.0, 0.0, 0.0, x_ouest, y_nord, 0.0), False),    # ModelTiepoint
        (34735, "H", len(geocles), geocles, False),                       # GeoKeyDirectory
    ]
    chemin.parent.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(chemin, altitudes.astype("<f4"), extratags=etiquettes,
                     rowsperstrip=altitudes.shape[0], compression=None)


if __name__ == "__main__":
    x0, y0 = CHEMINEE_A[0] - DEMI_COTE, CHEMINEE_A[1] - DEMI_COTE
    x1, y1 = CHEMINEE_A[0] + DEMI_COTE, CHEMINEE_A[1] + DEMI_COTE
    n = int(round(2 * DEMI_COTE / PAS))
    mnt = telecharger(x0, y0, x1, y1, n)
    if (mnt < -100).any():
        raise SystemExit("Le MNT contient des valeurs vides.")
    ecrire_geotiff(SORTIE, mnt, x0, y1, PAS)
    print(f"MNT {n}×{n} au pas de {PAS:.0f} m : {mnt.min():.1f} à {mnt.max():.1f} m")
    print(f"Altitude sous la cheminée A : {mnt[n // 2, n // 2]:.1f} m")
    print(f"Écrit : {SORTIE}")
