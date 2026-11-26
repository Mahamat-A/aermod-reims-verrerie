"""Cartes mensuelles de l'étape 8 (janvier, juillet 2024) : contribution de la verrerie O-I, quatre cas en 2 × 2.

Référence (Prunay, surface du mât) et WRF 1 km avec z0 0,25 m estimé autour de la source (variante ; la règle de l'EPA est la surface de la
maille WRF fournie par MMIF, z0 0,8 m, cas aermod/{jan,jul}_wrf_*), options rurale et urbaine. Mêmes règles que scripts/carte_aermod.py : une teinte, 5 classes rondes,
rien sous la première classe (≈ le quart du maximum), classes communes seulement entre cartes de même ordre.
Usage : carte_mois.py jan|jul
"""
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from carte_aermod import CHEMINEE, ETENDUE_FOND, PROJET, STATIONS, TEINTES, fond_gris, lire_plot, nord_et_echelle
from langue import fichier as nom_figure, nombre, t

CAS = {"prunay_rural": t("Prunay (référence), option rurale"),
       "prunay_urbain": t("Prunay, option urbaine"),
       "wrf-z025_rural": t("WRF 1 km, z0 0,25 m, option rurale"),
       "wrf-z025_urbain": t("WRF 1 km, z0 0,25 m, option urbaine")}
# Par mois : nom, z0 de Prunay, Bowen des variantes WRF, phrase sur les émissions, puis les classes de chaque carte
# (première classe ≈ le quart du maximum, arrondie)
MOIS = {
    "jan": dict(nom=t("janvier"), z0=t("0,03 m en hiver"), bowen=t("0,45"), emis="",
                moyenne={"prunay_rural": [0.05, 0.075, 0.1, 0.15, 0.2],      # max 0,25
                         "prunay_urbain": [0.1, 0.15, 0.2, 0.3, 0.4],        # 0,41
                         "wrf-z025_rural": [0.2, 0.3, 0.4, 0.6, 0.8],        # 0,87
                         "wrf-z025_urbain": [0.25, 0.4, 0.6, 0.8, 1.0]},     # 0,99
                max1h={"prunay_rural": [10, 15, 20, 30, 40],                 # 41,5
                       "prunay_urbain": [3, 4, 6, 8, 10],                    # 12,6
                       "wrf-z025_rural": [5, 8, 10, 15, 20],                 # 19,9
                       "wrf-z025_urbain": [4, 6, 8, 10, 12]}),               # 14,9
    "jul": dict(nom=t("juillet"), z0=t("0,15 m en été"), bowen=t("0,35"), emis=t(", four 3 arrêté le 12/07"),
                moyenne=dict.fromkeys(CAS, [0.1, 0.15, 0.2, 0.3, 0.4]),     # 0,39–0,65 : même ordre
                max1h={"prunay_rural": [5, 8, 10, 15, 20],                   # 21,8
                       "prunay_urbain": [2, 3, 4, 5, 6],                     # 7,5
                       "wrf-z025_rural": [2, 3, 4, 6, 8],                    # 9,2
                       "wrf-z025_urbain": [2.5, 4, 6, 8, 10]}),              # 10,6
}
CARTOUCHE = t(
    "AERMOD 26135, {nom} 2024 (744 h). Prunay : AERMET avec la surface autour du mât (z0 {z0}). "
    "WRF 4.7.1 (ERA5, 9/3/1 km) → MMIF 4.1.1 → AERMET, maille de la cheminée,\n"
    "z0 0,25 m estimé dans 1 km autour de la source, albédo 0,19, Bowen {bowen}. Cheminée 59 m, 523 K, 8 m/s, Ø 2,51 m ; "
    "NOx 2024 (IREP) modulés par mois{emis}.\nBâtiments BPIPPRM (BD TOPO), relief RGE ALTI 25 m. "
    "NO₂ ≈ 0,9 × NOx. Fond : Plan IGN (Géoplateforme)."
)
fr = lambda v: nombre(f"{v:g}")
NOM_FICHIER = {"jan": "janvier", "jul": "juillet"}


def panneau(ax, dossier, fichier, classes, note_max, sous_titre):
    xs, ys, c = lire_plot(PROJET / "aermod" / dossier / fichier)
    fond_gris(ax)
    ax.contourf(xs / 1000, ys / 1000, c, levels=classes + [np.inf], colors=TEINTES, alpha=0.72)
    ax.contour(xs / 1000, ys / 1000, c, levels=classes, colors="#5a0f0f", linewidths=0.5, alpha=0.8)
    ax.plot(CHEMINEE[0] / 1000, CHEMINEE[1] / 1000, "^", ms=10, mfc="k", mec="w", mew=1.3, zorder=5)
    for nom, (sx, sy) in STATIONS.items():
        ax.plot(sx / 1000, sy / 1000, "o", ms=6.5, mfc="w", mec="k", mew=1.1, zorder=5)
        ax.annotate(nom.split("\n")[0], (sx / 1000, sy / 1000), xytext=(-6, 5), textcoords="offset points",
                    fontsize=7, ha="right")
    i, j = np.unravel_index(np.nanargmax(c), c.shape)
    ax.plot(xs[j] / 1000, ys[i] / 1000, "P", ms=9, mfc="w", mec="k", zorder=5)
    ax.annotate("max. " + nombre(note_max.format(c[i, j])), (xs[j] / 1000, ys[i] / 1000),
                xytext=(6, 6), textcoords="offset points", fontsize=7.5,
                bbox=dict(fc="w", ec="0.6", lw=0.5, pad=1.2), zorder=6)
    poignees = [plt.Rectangle((0, 0), 1, 1, fc=t, alpha=0.72, ec="#5a0f0f", lw=0.5) for t in TEINTES]
    bornes = classes + [None]
    etiquettes = [f"{fr(bornes[k])} – {fr(bornes[k + 1])}" if bornes[k + 1] else f"≥ {fr(bornes[k])}"
                  for k in range(len(classes))]
    ax.legend(poignees, etiquettes, title="µg/m³", loc="lower right", fontsize=7, title_fontsize=7.5,
              framealpha=0.9)
    ax.set(xlim=(ETENDUE_FOND[0] / 1000, ETENDUE_FOND[1] / 1000),
           ylim=(ETENDUE_FOND[2] / 1000, ETENDUE_FOND[3] / 1000), aspect="equal")
    ax.set_xticks(np.arange(568, 587, 4))
    ax.set_yticks(np.arange(5444, 5464, 4))
    ax.tick_params(labelsize=7)
    ax.set_title(sous_titre, fontsize=10, loc="left")


def planche(mois, fichier, titre, classes, note_max, sortie):
    fig, axes = plt.subplots(2, 2, figsize=(12, 12.8))
    for ax, (cas, sous_titre) in zip(axes.flat, CAS.items()):
        panneau(ax, f"{mois}_{cas}", fichier, classes[cas], note_max, sous_titre)
    nord_et_echelle(axes[0, 0])
    fig.supxlabel("X UTM 31N, WGS 84 (km)", fontsize=9, y=0.075)
    fig.supylabel("Y UTM 31N, WGS 84 (km)", fontsize=9)
    fig.suptitle(titre, fontsize=12.5, x=0.02, ha="left")
    fig.text(0.02, 0.01, CARTOUCHE.format(**MOIS[mois]), fontsize=7, color="0.25", va="bottom")
    fig.tight_layout(rect=(0.01, 0.075, 1, 0.98), h_pad=2.5)
    fig.savefig(PROJET / "figures" / nom_figure(sortie), dpi=150)
    plt.close(fig)
    print(f"Écrit : figures/{nom_figure(sortie)}")


if __name__ == "__main__":
    mois = [a for a in sys.argv[1:] if not a.startswith("--")][0]
    m = MOIS[mois]
    planche(mois, "periode_grille.plt",
            t("NOx (éq. NO₂) – contribution de la verrerie O-I – moyenne de {mois} 2024").format(mois=m["nom"]),
            m["moyenne"], "{:.2f} µg/m³", f"etape8_{NOM_FICHIER[mois]}_moyenne.png")
    planche(mois, "max1h_grille.plt",
            t("NOx (éq. NO₂) – contribution de la verrerie O-I – maximum horaire de {mois} 2024").format(mois=m["nom"]),
            m["max1h"], "{:.0f} µg/m³", f"etape8_{NOM_FICHIER[mois]}_max1h.png")
