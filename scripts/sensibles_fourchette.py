"""NO₂ dû à la verrerie aux établissements sensibles, options rurale et urbaine (fourchette).

Entrées : donnees/sensibles/etablissements_sensibles.csv (points_sensibles.py) et les fichiers PLOTFILE
d'AERMOD (NO₂ OLM) de aermod/sensibles (urbain) et aermod/sensibles_rural (rural).
Sortie : base/sensibles.csv, chargé dans PostgreSQL par base/requetes/risques_sanitaires.sql.
"""

from pathlib import Path

import pandas as pd

PROJET = Path(__file__).resolve().parent.parent
CAS = {"urbain": "sensibles", "rural": "sensibles_rural"}
DUREES = {"annuel": "no2_annuel.plt", "max24h": "no2_max24h.plt", "max1h": "no2_max1h.plt"}


def lire_plt(chemin):
    lignes = [l.split() for l in chemin.open() if not l.startswith("*")]
    return {(round(float(l[0]), 1), round(float(l[1]), 1)): float(l[2]) for l in lignes}


if __name__ == "__main__":
    e = pd.read_csv(PROJET / "donnees/sensibles/etablissements_sensibles.csv")
    for option, dossier in CAS.items():
        for duree, fichier in DUREES.items():
            valeurs = lire_plt(PROJET / "aermod" / dossier / fichier)
            e[f"no2_{duree}_{option}"] = [valeurs[(round(x, 1), round(y, 1))] for x, y in zip(e.x, e.y)]
    colonnes = ["id", "type", "nom", "distance_m", "x", "y"] + [f"no2_{d}_{o}" for o in CAS for d in DUREES]
    e[colonnes].to_csv(PROJET / "base/sensibles.csv", index=False, float_format="%.5f")
    print(f"{len(e)} établissements écrits dans base/sensibles.csv")
    print(e[[c for c in colonnes if c.startswith("no2_")]].max().round(3).to_string())
