"""Mesures horaires 2024 des 3 stations ATMO Grand Est de Reims : lecture, contrôle, synthèse.

Entrée : observations/brut/reims_AAAA-MM-JJ.csv (extraits des fichiers E2 du LCSQA).
Sortie : observations/reims_2024_horaire.csv, une ligne par heure (début d'heure, UTC),
une colonne par station et polluant ; seules les valeurs validées (validité = 1) sont gardées.
"""

from pathlib import Path

import pandas as pd

PROJET = Path(__file__).resolve().parent.parent
BRUT = PROJET / "observations" / "brut"
SORTIE = PROJET / "observations" / "reims_2024_horaire.csv"
STATIONS = {"FR14012": "jean_daulan", "FR14011": "doumer", "FR14010": "betheny"}
POLLUANTS = {"NO": "no", "NO2": "no2", "NOX as NO2": "nox", "O3": "o3"}
# L'en-tête E2 commence par un BOM : le filtre du téléchargement ne l'a pas gardé, on le redonne ici.
COLONNES = ["Date de début", "Date de fin", "Organisme", "code zas", "Zas", "code site", "nom site",
            "type d'implantation", "Polluant", "type d'influence", "discriminant", "Réglementaire",
            "type d'évaluation", "procédure de mesure", "type de valeur", "valeur", "valeur brute",
            "unité de mesure", "taux de saisie", "couverture temporelle", "couverture de données",
            "code qualité", "validité"]


def lire():
    morceaux = [pd.read_csv(f, sep=";", header=None, names=COLONNES, dtype=str) for f in sorted(BRUT.glob("reims_*.csv"))]
    brut = pd.concat(morceaux, ignore_index=True)
    brut = brut[brut["code site"].isin(STATIONS) & brut["Polluant"].isin(POLLUANTS)]
    total = len(brut)
    brut = brut[brut["validité"] == "1"]
    brut["debut"] = pd.to_datetime(brut["Date de début"], format="%Y/%m/%d %H:%M:%S")
    brut["valeur"] = pd.to_numeric(brut["valeur"], errors="coerce")
    brut["colonne"] = brut["code site"].map(STATIONS) + "_" + brut["Polluant"].map(POLLUANTS)
    horaire = brut.pivot_table(index="debut", columns="colonne", values="valeur", aggfunc="first")
    heures = pd.date_range("2024-01-01 00:00", "2024-12-31 23:00", freq="h")
    return horaire.reindex(heures).rename_axis("debut_utc"), total, len(brut)


if __name__ == "__main__":
    horaire, total, valides = lire()
    horaire.to_csv(SORTIE, float_format="%.1f")
    print(f"Lignes lues : {total}, validées : {valides} ({100 * valides / total:.1f} %)")
    print(f"Écrit : {SORTIE}\n")
    synthese = pd.DataFrame({
        "couverture_%": 100 * horaire.notna().mean(),
        "moyenne_µg/m³": horaire.mean(),
        "P98_µg/m³": horaire.quantile(0.98),
        "max_µg/m³": horaire.max(),
    }).round(1)
    print(synthese.to_string())
