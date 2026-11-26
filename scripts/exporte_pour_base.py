"""Prépare les CSV à charger dans PostgreSQL (base oi_reims), au format « long » : une ligne = une valeur.

- base/mesures.csv : station, polluant, debut_utc, valeur (µg/m³), mesures ATMO validées 2024
- base/meteo.csv   : debut_utc, vitesse (m/s), direction (°), monin_obukhov (m), zi_conv (m), zi_meca (m)
- base/modele.csv  : cas, station, debut_utc, nox (µg/m³), contribution AERMOD de la verrerie
Toutes les heures sont ramenées en UTC, début d'heure (convention des mesures).
"""

import sys
from pathlib import Path

import pandas as pd

PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJET / "scripts"))
from compare_secteurs import X_STATIONS  # noqa: E402

BASE = PROJET / "base"
CODES = {"jean_daulan": "FR14012", "doumer": "FR14011", "betheny": "FR14010"}


def debut_utc_depuis_lst(an, mois, jour, heure_fin):
    """Heure AERMET/AERMOD (locale standard UTC+1, heure de fin 1–24) → début d'heure en UTC."""
    return pd.Timestamp(year=an, month=mois, day=jour) + pd.Timedelta(hours=heure_fin - 2)


if __name__ == "__main__":
    obs = pd.read_csv(PROJET / "observations/reims_2024_horaire.csv", parse_dates=["debut_utc"], index_col=0)
    longues = obs.stack().rename("valeur").dropna().reset_index()   # pas de ligne sans valeur
    longues[["station", "polluant"]] = longues["level_1"].str.rsplit("_", n=1, expand=True)
    longues["station"] = longues["station"].map(CODES)
    longues[["station", "polluant", "debut_utc", "valeur"]].to_csv(BASE / "mesures.csv", index=False)

    lignes = [l.split() for l in list((PROJET / "aermet/prunay_2024.sfc").open())[1:]]
    meteo = pd.DataFrame({
        "debut_utc": [debut_utc_depuis_lst(int(l[0]), int(l[1]), int(l[2]), int(l[4])) for l in lignes],
        "vitesse": [float(l[15]) for l in lignes], "direction": [float(l[16]) for l in lignes],
        "monin_obukhov": [float(l[11]) for l in lignes], "zi_conv": [float(l[9]) for l in lignes],
        "zi_meca": [float(l[10]) for l in lignes]})
    # Codes « manquant » d'AERMET → valeur vide (NULL dans la base)
    for colonne, code in [("zi_conv", -999.0), ("zi_meca", -999.0), ("monin_obukhov", -99999.0),
                          ("vitesse", 999.0), ("direction", 999.0)]:
        meteo.loc[meteo[colonne] == code, colonne] = None
    meteo.to_csv(BASE / "meteo.csv", index=False)

    morceaux = []
    for cas, fichier in [("rural", "aermod/reference_bati/horaire_stations.pst"),
                         ("urbain", "aermod/reference_urbaine/horaire_stations.pst")]:
        p = [l.split() for l in (PROJET / fichier).open() if not l.startswith("*")]
        morceaux.append(pd.DataFrame({
            "cas": cas,
            "station": [CODES[X_STATIONS[round(float(l[0]), 1)]] for l in p],
            "debut_utc": [debut_utc_depuis_lst(2000 + int(l[8][:2]), int(l[8][2:4]), int(l[8][4:6]), int(l[8][6:8])) for l in p],
            "nox": [float(l[2]) for l in p]}))
    pd.concat(morceaux).to_csv(BASE / "modele.csv", index=False)
    for f in ("mesures", "meteo", "modele"):
        print(f"{f}.csv : {sum(1 for _ in (BASE / f'{f}.csv').open()) - 1} lignes")
