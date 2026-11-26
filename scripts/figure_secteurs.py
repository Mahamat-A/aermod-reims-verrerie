"""Étape 6 : NO2 mesuré et contribution modélisée de la verrerie, selon la direction du vent.

Une colonne par station, deux lignes : en haut le NO2 mesuré, en bas la contribution AERMOD
(NO2, méthode OLM, bâtiments inclus). Échelles verticales séparées : les deux grandeurs
diffèrent d'un facteur ~50 ; la bande grise marque la direction de l'usine (± 15°).
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJET / "scripts"))
from compare_secteurs import DIRECTION_USINE, X_STATIONS, cle_aermod, lire_meteo  # noqa: E402

NOMS = {"jean_daulan": "Jean d'Aulan (fond urbain)", "doumer": "Doumer (trafic)",
        "betheny": "Bétheny (fond périurbain)"}
ROUGE, GRIS = "#cc3a2c", "#3a3a3a"


def modele_no2():
    lignes = [l.split() for l in (PROJET / "aermod/no2/OLM_urbain_horaire_stations.pst").open() if not l.startswith("*")]
    m = pd.DataFrame({"station": [X_STATIONS[round(float(l[0]), 1)] for l in lignes],
                      "cle": [l[8] for l in lignes], "no2": [float(l[2]) for l in lignes]})
    return m.pivot(index="cle", columns="station", values="no2").add_suffix("_modele")


def tableau():
    obs = pd.read_csv(PROJET / "observations/reims_2024_horaire.csv", parse_dates=["debut_utc"], index_col=0)
    obs["cle"] = cle_aermod(obs.index)
    t = obs.join(modele_no2(), on="cle").join(lire_meteo(), on="cle")
    t = t[t["direction"] > 0]
    t["secteur"] = (np.floor(t["direction"] / 10) * 10 + 5) % 360
    return t


if __name__ == "__main__":
    t = tableau()
    fig, axes = plt.subplots(2, 3, figsize=(14, 6.8), sharex=True)
    for k, (s, d) in enumerate(DIRECTION_USINE.items()):
        g = t.groupby("secteur")
        mesure, modele = g[f"{s}_no2"].mean(), g[f"{s}_modele"].mean()
        n = g[f"{s}_no2"].count()
        for ax in axes[:, k]:
            ax.axvspan(d - 15, d + 15, color="0.88", zorder=0)
            ax.grid(axis="y", color="0.9", lw=0.6)
            ax.spines[["top", "right"]].set_visible(False)
        axes[0, k].plot(mesure.index, mesure.values, color=GRIS, lw=2, marker="o", ms=3)
        axes[0, k].set_title(NOMS[s], fontsize=11, loc="left")
        axes[0, k].set_ylim(0, None)
        axes[1, k].plot(modele.index, modele.values, color=ROUGE, lw=2, marker="o", ms=3)
        axes[1, k].set_ylim(0, modele.max() * 1.18)
        axes[1, k].text(d + 17, modele.max() * 1.1, "direction\nde l'usine", ha="left", va="top", fontsize=8, color="0.35")
        axes[1, k].set_xlabel("Direction d'où vient le vent (°)")
        axes[1, k].set_xticks(range(0, 361, 90))
        print(f"{s:12s} secteur usine : NO2 mesuré {mesure.loc[[v for v in mesure.index if abs(((v - d + 180) % 360) - 180) <= 15]].mean():5.1f} | "
              f"modèle {modele.loc[[v for v in modele.index if abs(((v - d + 180) % 360) - 180) <= 15]].mean():.2f} µg/m³ | heures/secteur min {n.min()}")
    axes[0, 0].set_ylabel("NO₂ mesuré (µg/m³)")
    axes[1, 0].set_ylabel("Contribution modélisée\nde la verrerie, NO₂ (µg/m³)")
    fig.suptitle("Reims 2024 – NO₂ moyen par secteur de vent de 10° (vent : Reims-Prunay) : "
                 "mesures ATMO Grand Est et contribution AERMOD de la verrerie O-I", fontsize=11.5)
    fig.text(0.01, 0.005, "Mesures : LCSQA/ATMO Grand Est, valeurs validées. Modèle : AERMOD 26135, OLM "
             "(ozone mesuré, NO₂/NOx à l'émission 0,10), option urbaine, bâtiments BPIPPRM. Échelles verticales différentes "
             "(facteur ~50).", fontsize=7.5, color="0.3")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(PROJET / "figures" / "etape6_secteurs_no2.png", dpi=150)
    print("Écrit : figures/etape6_secteurs_no2.png")
