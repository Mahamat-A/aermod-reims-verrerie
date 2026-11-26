"""Étape 7 : effet de chaque test de sensibilité (un paramètre à la fois) sur trois indicateurs."""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJET = Path(__file__).resolve().parent.parent
AERMOD = PROJET / "aermod"
LIBELLES = {
    "urbain_182000": "Option urbaine (182 000 hab.)",
    "temperature_473K": "Fumées à 200 °C (au lieu de 250)",
    "temperature_573K": "Fumées à 300 °C",
    "diametre_1.5m": "Diamètre 1,5 m (vitesse 22 m/s)",
    "juillet_horaire": "Juillet heure par heure (HOUREMIS)",
    "position_B": "Cheminée en position B",
    "sans_batiments": "Sans les bâtiments",
}
HAUSSE, BAISSE = "#cc3a2c", "#3b6ea8"


def lire(f):
    return np.array([float(l.split()[2]) for l in f.open() if not l.startswith("*")])


def indicateurs(dossier):
    return {"Maximum annuel (grille)": lire(dossier / "annuel_grille.plt").max(),
            "Maximum horaire (grille)": lire(dossier / "max1h_grille.plt").max(),
            "Moyenne annuelle aux 3 stations": lire(dossier / "annuel_stations.plt").mean()}


if __name__ == "__main__":
    ref = indicateurs(AERMOD / "reference_bati")
    ecarts = {n: {k: 100 * (v / ref[k] - 1) for k, v in indicateurs(AERMOD / "sensibilite" / n).items()}
              for n in LIBELLES}
    ordre = sorted(LIBELLES, key=lambda n: max(abs(v) for v in ecarts[n].values()))
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True)
    for ax, k in zip(axes, ref):
        vals = [ecarts[n][k] for n in ordre]
        ax.barh(range(len(ordre)), vals, color=[HAUSSE if v > 0 else BAISSE for v in vals], height=0.6)
        ax.axvline(0, color="0.3", lw=0.8)
        lim = max(abs(v) for v in vals) * 1.35
        ax.set_xlim(-lim, lim)
        for i, v in enumerate(vals):
            ax.text(v + (lim * 0.03 if v >= 0 else -lim * 0.03), i, (f"{v:+.0f} %" if round(v) != 0 else "0 %"), va="center",
                    ha="left" if v >= 0 else "right", fontsize=8.5)
        unite = "µg/m³"
        ax.set_title(f"{k}\nréférence : {ref[k]:.3g} {unite}".replace(".", ","), fontsize=10, loc="left")
        ax.grid(axis="x", color="0.9", lw=0.6)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel("Écart à la référence (%)")
    axes[0].set_yticks(range(len(ordre)), [LIBELLES[n] for n in ordre])
    fig.suptitle("Sensibilité d'AERMOD aux hypothèses – NOx de la verrerie O-I, 2024 (un paramètre modifié à la fois)",
                 fontsize=11.5)
    fig.tight_layout()
    fig.savefig(PROJET / "figures" / "etape7_sensibilite.png", dpi=150)
    print("Écrit : figures/etape7_sensibilite.png")
