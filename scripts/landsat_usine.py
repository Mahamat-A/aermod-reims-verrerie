"""Température de surface Landsat 8/9 (Collection 2 niveau 2, bande ST_B10) autour de la verrerie O-I.

But : estimer l'excès de température de l'usine (« îlot de chaleur industriel », Paine et al., 2016) pour juger si
l'option urbaine d'AERMOD se justifie près de la source. Données : Microsoft Planetary Computer (STAC public,
URL signées anonymement). Lit seulement une fenêtre de 6 × 6 km par scène (lecture partielle des COG).
Sortie : donnees/landsat/st_<date>.npz (température en K, grille UTM 31N à 30 m) et un tableau des scènes.
"""
import json
from pathlib import Path

import numpy as np
import rasterio
import requests
from rasterio.windows import from_bounds

PROJET = Path(__file__).resolve().parent.parent
SORTIE = PROJET / "donnees/landsat"
X0, Y0 = 576601.2, 5453845.2
DEMI = 3000.0
ECHELLE, DECALAGE = 0.00341802, 149.0
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
JETON = "https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2"
_jeton = {}


def chercher():
    corps = {"collections": ["landsat-c2-l2"], "intersects": {"type": "Point", "coordinates": [4.0522, 49.2326]},
             "datetime": "2022-01-01T00:00:00Z/2026-11-20T00:00:00Z", "limit": 200,
             "query": {"eo:cloud_cover": {"lt": 20}, "platform": {"in": ["landsat-8", "landsat-9"]}}}
    r = requests.post(STAC, json=corps, timeout=120)
    r.raise_for_status()
    return sorted(r.json()["features"], key=lambda i: i["properties"]["datetime"])


def lire(href):
    # Jeton SAS anonyme et public de la collection (aucun compte), demandé une fois puis réutilisé
    if "t" not in _jeton:
        _jeton["t"] = requests.get(JETON, timeout=60).json()["token"]
    url = f"{href}?{_jeton['t']}"
    with rasterio.open(url) as src:
        assert src.crs.to_epsg() == 32631, src.crs
        fen = from_bounds(X0 - DEMI, Y0 - DEMI, X0 + DEMI, Y0 + DEMI, src.transform)
        return src.read(1, window=fen), src.window_transform(fen)


if __name__ == "__main__":
    SORTIE.mkdir(parents=True, exist_ok=True)
    resume = []
    for it in chercher():
        date = it["properties"]["datetime"][:10]
        if (SORTIE / f"st_{date}.npz").exists():
            continue
        st, transform = lire(it["assets"]["lwir11"]["href"])
        qa, _ = lire(it["assets"]["qa_pixel"]["href"])
        # QA_PIXEL : bit 6 = clair ; on exige le ciel clair sur toute la fenêtre de 6 km
        clair = (qa & (1 << 6)) > 0
        temp = np.where((st > 0) & clair, st * ECHELLE + DECALAGE, np.nan).astype(np.float32)
        part = float(np.isfinite(temp).mean())
        resume.append({"date": date, "id": it["id"], "nuages_scene": it["properties"]["eo:cloud_cover"],
                       "clair_fenetre": round(part, 3)})
        if part > 0.98:
            np.savez_compressed(SORTIE / f"st_{date}.npz", t=temp, transform=np.array(transform)[:6])
        print(f"{date}  fenêtre claire à {100 * part:5.1f} %", flush=True)
    (SORTIE / "scenes.json").write_text(json.dumps(resume, indent=1))
