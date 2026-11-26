"""Cartes AERMOD 2024 (NOx de la verrerie O-I), au format rapport, options urbaine et rurale.

Règles convenues pour toutes les cartes du projet : une seule teinte du clair au foncé, 5 classes
rondes, rien de coloré sous la première classe (on ne montre que là où l'usine compte), et des classes
propres à chaque carte, adaptées à ses valeurs. Seules les deux moyennes annuelles, de même ordre de
grandeur, partagent leurs classes ; les maxima horaires (14 et 49 µg/m³) ont chacun les leurs.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

from langue import fichier as nom_figure, nombre, t

PROJET = Path(__file__).resolve().parent.parent
OPTIONS = {"urbaine": (PROJET / "aermod" / "reference_urbaine",
                       t("option urbaine (182 000 hab. ; densité ~3 000 hab/km² dans un rayon de 3 km)")),
           "rurale": (PROJET / "aermod" / "reference_bati",
                      t("option rurale (méthode d'Auer : 24 % de sols urbains dans un rayon de 3 km)"))}
FOND = PROJET / "donnees" / "relief" / "plan_ign_20km.png"
ETENDUE_FOND = (566476.2, 586726.2, 5443720.2, 5463970.2)   # m, UTM 31N (WMS Plan IGN)
CHEMINEE = (576601.2, 5453845.2)
STATIONS = {t("Jean d'Aulan\n(fond urbain)"): (574309.9, 5452877.0),
            t("Doumer\n(trafic)"): (574452.6, 5455832.7),
            t("Bétheny\n(fond périurbain)"): (576445.0, 5459361.1)}
# Une seule teinte, du clair au foncé (5 classes)
TEINTES = ["#fcd9c4", "#f7a582", "#ec6f4f", "#cc3a2c", "#8e1616"]
CARTOUCHE = t(
    "AERMOD 26135 – météo Reims-Prunay 2024 (AERMET, radiosondages Trappes / Idar-Oberstein) – "
    "relief IGN RGE ALTI 25 m\n"
    "Source : cheminée 59 m, 523 K, 8 m/s, Ø 2,51 m ; 143 t NOx en 2024 (IREP), modulées par mois "
    "(arrêt du four 3 le 12/07)\n"
    "Sillage des bâtiments : BPIPPRM, BD TOPO IGN ; {option}\n"
    "NO₂ ≈ 0,9 × NOx (OLM, ozone en excès). Fond : Plan IGN (Géoplateforme)"
)


def lire_plot(chemin):
    """Points de la grille (pas de 250 m) d'un PLOTFILE AERMOD : x, y (m), concentration."""
    a = np.array([[float(v) for v in l.split()[:3]] for l in chemin.open() if not l.startswith("*")])
    sur_grille = ((np.abs((a[:, 0] - CHEMINEE[0] + 1e-6) % 250) < 0.1)
                  & (np.abs((a[:, 1] - CHEMINEE[1] + 1e-6) % 250) < 0.1))
    a = a[sur_grille]
    xs, ys = np.unique(a[:, 0]), np.unique(a[:, 1])
    c = np.full((ys.size, xs.size), np.nan)
    c[np.searchsorted(ys, a[:, 1]), np.searchsorted(xs, a[:, 0])] = a[:, 2]
    return xs, ys, c


def fond_gris(ax):
    rgb = plt.imread(FOND)[..., :3]
    gris = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    ax.imshow(0.55 + 0.45 * gris, cmap="gray", vmin=0, vmax=1,
              extent=[v / 1000 for v in ETENDUE_FOND], interpolation="bilinear")


def nord_et_echelle(ax):
    ax.annotate("N", xy=(0.95, 0.95), xytext=(0.95, 0.87), xycoords="axes fraction",
                ha="center", fontsize=12, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.5))
    x0, y0 = ETENDUE_FOND[0] / 1000 + 1.0, ETENDUE_FOND[2] / 1000 + 0.8
    for i in range(2):
        ax.add_patch(plt.Rectangle((x0 + i, y0), 1, 0.15, fc="k" if i == 0 else "w", ec="k", lw=0.8))
    ax.text(x0, y0 + 0.3, "0", ha="center", fontsize=8)
    ax.text(x0 + 2, y0 + 0.3, "2 km", ha="center", fontsize=8)


def carte(option, fichier, titre, classes, sortie, note_max):
    cas, texte_option = OPTIONS[option]
    xs, ys, c = lire_plot(cas / fichier)
    fig, ax = plt.subplots(figsize=(9, 9.6))
    fond_gris(ax)
    palette = ListedColormap(TEINTES)
    niveaux = classes + [np.inf]
    ax.contourf(xs / 1000, ys / 1000, c, levels=niveaux, colors=TEINTES, alpha=0.72)
    ax.contour(xs / 1000, ys / 1000, c, levels=classes, colors="#5a0f0f", linewidths=0.5, alpha=0.8)

    ax.plot(CHEMINEE[0] / 1000, CHEMINEE[1] / 1000, "^", ms=12, mfc="k", mec="w", mew=1.5, zorder=5)
    ax.annotate(t("Verrerie O-I\n(cheminée 59 m)"), (CHEMINEE[0] / 1000, CHEMINEE[1] / 1000),
                xytext=(10, -22), textcoords="offset points", fontsize=8.5, fontweight="bold")
    for nom, (sx, sy) in STATIONS.items():
        ax.plot(sx / 1000, sy / 1000, "o", ms=8, mfc="w", mec="k", mew=1.3, zorder=5)
        ax.annotate(nom, (sx / 1000, sy / 1000), xytext=(-8, 6), textcoords="offset points",
                    fontsize=8, ha="right")
    i, j = np.unravel_index(np.nanargmax(c), c.shape)
    ax.plot(xs[j] / 1000, ys[i] / 1000, "P", ms=11, mfc="w", mec="k", zorder=5)
    ax.annotate("max. " + nombre(note_max.format(c[i, j])), (xs[j] / 1000, ys[i] / 1000),
                xytext=(8, 8), textcoords="offset points", fontsize=8.5,
                bbox=dict(fc="w", ec="0.6", lw=0.5, pad=1.5))

    poignees = [plt.Rectangle((0, 0), 1, 1, fc=t, alpha=0.72, ec="#5a0f0f", lw=0.5) for t in TEINTES]
    bornes = classes + [None]
    fr = lambda v: nombre(f"{v:g}")
    etiquettes = [f"{fr(bornes[k])} – {fr(bornes[k + 1])}" if bornes[k + 1] else f"≥ {fr(bornes[k])}"
                  for k in range(len(classes))]
    ax.legend(poignees, etiquettes, title="µg/m³", loc="lower right", fontsize=8.5,
              title_fontsize=9, framealpha=0.9)
    nord_et_echelle(ax)
    ax.set(xlim=(ETENDUE_FOND[0] / 1000, ETENDUE_FOND[1] / 1000),
           ylim=(ETENDUE_FOND[2] / 1000, ETENDUE_FOND[3] / 1000), aspect="equal",
           xlabel="X UTM 31N, WGS 84 (km)", ylabel="Y UTM 31N, WGS 84 (km)")
    ax.set_xticks(np.arange(568, 587, 2))
    ax.set_yticks(np.arange(5444, 5464, 2))
    ax.set_title(titre, fontsize=12, loc="left")
    fig.text(0.02, 0.012, CARTOUCHE.format(option=texte_option), fontsize=7, color="0.25", va="bottom")
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    fig.savefig(PROJET / "figures" / nom_figure(sortie), dpi=170)
    plt.close(fig)
    print(f"Écrit : figures/{nom_figure(sortie)}")


if __name__ == "__main__":
    # première classe ≈ le quart du maximum (14 et 49 µg/m³), arrondi : on ne colore que là où l'usine compte
    classes_horaires = {"urbaine": [4, 6, 8, 10, 12], "rurale": [10, 15, 20, 30, 40]}
    for option, prefixe in [("urbaine", "aermod_reference_2024"), ("rurale", "aermod_rural_2024")]:
        carte(option, "annuel_grille.plt",
              t("NOx (éq. NO₂) – contribution de la verrerie O-I – moyenne annuelle 2024 – option {option}").format(option=t(option)),
              [0.05, 0.075, 0.1, 0.15, 0.2], f"{prefixe}_annuel.png", "{:.2f} µg/m³")
        carte(option, "max1h_grille.plt",
              t("NOx (éq. NO₂) – contribution de la verrerie O-I – maximum horaire 2024 – option {option}").format(option=t(option)),
              classes_horaires[option], f"{prefixe}_max1h.png", "{:.0f} µg/m³")
