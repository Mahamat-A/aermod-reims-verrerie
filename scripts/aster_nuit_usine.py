"""Température de surface ASTER de NUIT (AST_08, version 4, 90 m) autour de la verrerie O-I.

Complète scripts/landsat_usine.py (images de jour) : la nuit, le soleil ne chauffe plus les toits, l'excès de
température de l'usine reflète la chaleur des procédés (critère « îlot de chaleur industriel » de Paine et al.,
2016 : ΔT ≥ 8 K sur quelques centaines de mètres). Catalogue NASA CMR (public) ; téléchargement LP DAAC avec un
jeton Earthdata lu dans ~/.earthdata_token (jamais affiché). Sortie : donnees/aster/skt_<date>.tif (scène entière,
~1 Mo) et donnees/aster/scenes.json (couverture nuageuse estimée par AST_L1T).
"""
import json
from pathlib import Path

import requests

PROJET = Path(__file__).resolve().parent.parent
SORTIE = PROJET / "donnees/aster"
CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
POINT = "4.0522,49.2326"


def granules(nom):
    r = requests.get(CMR, params={"short_name": nom, "point": POINT, "day_night_flag": "night",
                                  "page_size": 200, "sort_key": "start_date"}, timeout=120)
    r.raise_for_status()
    return r.json()["feed"]["entry"]


if __name__ == "__main__":
    SORTIE.mkdir(parents=True, exist_ok=True)
    jeton = (Path.home() / ".earthdata_token").read_text().strip()
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {jeton}"
    # Couverture nuageuse : estimée sur la scène L1T de même identifiant d'acquisition
    nuages = {g["producer_granule_id"][8:31]: float(g.get("cloud_cover", "nan")) for g in granules("AST_L1T")}
    resume = []
    for g in granules("AST_08"):
        cle = g["producer_granule_id"][7:30]
        date = g["time_start"][:16].replace(":", "")
        lien = next(l["href"] for l in g["links"] if l["href"].startswith("https") and l["href"].endswith("_SKT.tif"))
        f = SORTIE / f"skt_{date}.tif"
        if not f.exists():
            r = session.get(lien, timeout=600)
            if r.status_code != 200 or not r.content.startswith((b"II", b"MM")):
                print(f"{date} : échec du téléchargement (HTTP {r.status_code})", flush=True)
                continue
            f.write_bytes(r.content)
        resume.append({"date": date, "fichier": f.name, "nuages_L1T": nuages.get(cle)})
        print(f"{date} : {f.stat().st_size / 1e6:.1f} Mo, nuages L1T {nuages.get(cle)}", flush=True)
    (SORTIE / "scenes.json").write_text(json.dumps(resume, indent=1))
