"""Mesures ATMO vs contribution AERMOD de la verrerie, selon la direction du vent (2024).

Alignement des heures : mesures = début d'heure en UTC ; AERMOD et AERMET = heure locale
standard (UTC+1), heure de fin (1 à 24). Une mesure qui commence à t (UTC) correspond donc
à l'heure AERMOD qui finit à t + 2 h en heure locale.
"""

from pathlib import Path

import numpy as np
import pandas as pd

PROJET = Path(__file__).resolve().parent.parent
X_STATIONS = {574309.9: "jean_daulan", 574452.6: "doumer", 576445.0: "betheny"}
DIRECTION_USINE = {"jean_daulan": 67, "doumer": 133, "betheny": 178}   # d'où vient le vent


def cle_aermod(debut_utc):
    fin_lst = debut_utc + pd.Timedelta(hours=2)
    jour = fin_lst - pd.Timedelta(hours=1)          # l'heure 24 appartient à la veille
    heure = np.where(fin_lst.hour == 0, 24, fin_lst.hour)
    return jour.strftime("%y%m%d") + pd.Series(heure, index=debut_utc).map("{:02d}".format).values


def lire_modele():
    lignes = [l.split() for l in (PROJET / "aermod/reference/horaire_stations.pst").open() if not l.startswith("*")]
    m = pd.DataFrame({"station": [X_STATIONS[round(float(l[0]), 1)] for l in lignes],
                      "cle": [l[8] for l in lignes], "modele": [float(l[2]) for l in lignes]})
    return m.pivot(index="cle", columns="station", values="modele")


def lire_meteo():
    lignes = [l.split() for l in list((PROJET / "aermet/prunay_2024.sfc").open())[1:]]
    return pd.DataFrame({"cle": [f"{l[0][2:]}{int(l[1]):02d}{int(l[2]):02d}{int(l[4]):02d}" for l in lignes],
                         "vitesse": [float(l[15]) for l in lignes],
                         "direction": [float(l[16]) for l in lignes]}).set_index("cle")


def tableau():
    obs = pd.read_csv(PROJET / "observations/reims_2024_horaire.csv", parse_dates=["debut_utc"], index_col=0)
    obs["cle"] = cle_aermod(obs.index)
    return obs.join(lire_modele(), on="cle").join(lire_meteo(), on="cle")


if __name__ == "__main__":
    t = tableau()
    print(f"heures appariées avec la météo : {t['direction'].notna().sum()} / {len(t)}\n")
    for s, d_usine in DIRECTION_USINE.items():
        ok = t[[f"{s}_nox", s, "direction"]].dropna()
        ok = ok[ok["direction"] > 0]
        ecart = ((ok["direction"] - d_usine + 180) % 360) - 180
        dans = ok[ecart.abs() <= 15]
        voisins = ok[(ecart.abs() > 15) & (ecart.abs() <= 45)]
        print(f"{s:12s} vent de l'usine ({d_usine}° ± 15°) : {len(dans):4d} h | "
              f"NOx mesuré {dans[f'{s}_nox'].mean():5.1f} µg/m³ (secteurs voisins {voisins[f'{s}_nox'].mean():5.1f}) | "
              f"contribution modélisée {dans[s].mean():5.2f} µg/m³ (voisins {voisins[s].mean():5.2f})")
