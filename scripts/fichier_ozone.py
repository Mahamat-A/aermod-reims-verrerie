"""Fichier d'ozone horaire pour AERMOD (OLM/GRSM) : Jean d'Aulan, complété par Bétheny.

Les heures sont converties en heure locale standard, heure de fin (comme AERMET/AERMOD).
Une heure sans mesure aux deux stations est écrite -9 : AERMOD prend alors la valeur
de remplacement donnée par CO OZONEVAL.
"""

import sys
from pathlib import Path

import pandas as pd

PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJET / "scripts"))
from compare_secteurs import cle_aermod  # noqa: E402

SORTIE = PROJET / "aermod" / "no2" / "ozone_reims_2024.txt"

if __name__ == "__main__":
    obs = pd.read_csv(PROJET / "observations/reims_2024_horaire.csv", parse_dates=["debut_utc"], index_col=0)
    o3 = obs["jean_daulan_o3"].fillna(obs["betheny_o3"])
    o3.index = cle_aermod(obs.index)
    lignes = [l.split() for l in list((PROJET / "aermet/prunay_2024.sfc").open())[1:]]
    with SORTIE.open("w") as f:
        manquantes = 0
        for l in lignes:
            cle = f"{l[0][2:]}{int(l[1]):02d}{int(l[2]):02d}{int(l[4]):02d}"
            v = o3.get(cle)
            if v is None or pd.isna(v):
                v, manquantes = -9.0, manquantes + 1
            f.write(f"{l[0][2:]} {int(l[1]):2d} {int(l[2]):2d} {int(l[4]):2d} {v:7.1f}\n")
    print(f"{len(lignes)} heures écrites, dont {manquantes} sans mesure (-9) ; moyenne O3 {o3.mean():.1f} µg/m³")
    print(f"Écrit : {SORTIE}")
