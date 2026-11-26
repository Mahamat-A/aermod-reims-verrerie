"""Figure du relief (MNT IGN RGE ALTI 25 m, scripts/prepare_mnt.py) et du domaine des récepteurs AERMOD.

Carré de 30 km centré sur la cheminée, ombrage du relief, isolignes tous les 25 m, domaine des récepteurs (20 × 20 km)
en tirets, stations ATMO. Sortie : figures/relief_recepteurs.png (option --en : relief_recepteurs_en.png).
"""
from pathlib import Path

import matplotlib
import numpy as np
import rasterio

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

from langue import fichier, t

PROJET = Path(__file__).resolve().parent.parent
CHEMINEE = (576601.2, 5453845.2)
STATIONS = {"Jean d'Aulan": (574309.9, 5452877.0), "Doumer": (574452.6, 5455832.7), "Bétheny": (576445.0, 5459361.1)}
# décalage de l'étiquette (points) : Jean d'Aulan à gauche, pour ne pas masquer la cheminée
DECALAGE = {"Jean d'Aulan": (-6, -14, "right"), "Doumer": (6, 5, "left"), "Bétheny": (6, 5, "left")}

if __name__ == "__main__":
    with rasterio.open(PROJET / "donnees/relief/mnt_ign_25m_utm31n.tif") as src:
        z, b = src.read(1).astype(float), src.bounds
    etendue = [(b.left - CHEMINEE[0]) / 1000, (b.right - CHEMINEE[0]) / 1000,
               (b.bottom - CHEMINEE[1]) / 1000, (b.top - CHEMINEE[1]) / 1000]
    fig, ax = plt.subplots(figsize=(7.5, 6.4))
    ombre = LightSource(azdeg=315, altdeg=45).shade(z, cmap=plt.get_cmap("terrain"), vmin=40, vmax=300,
                                                    vert_exag=3, blend_mode="soft")
    ax.imshow(ombre, extent=etendue, origin="upper")
    x = np.linspace(etendue[0], etendue[1], z.shape[1])
    y = np.linspace(etendue[3], etendue[2], z.shape[0])
    ax.contour(x, y, z, levels=np.arange(75, 300, 25), colors="k", linewidths=0.3, alpha=0.4)
    image = ax.imshow(z, extent=etendue, cmap="terrain", vmin=40, vmax=300, alpha=0)
    barre = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    barre.solids.set_alpha(1)
    barre.set_label(t("Altitude (m)"))
    ax.plot([-10, 10, 10, -10, -10], [-10, -10, 10, 10, -10], "k--", lw=1.2)
    for nom, (sx, sy) in STATIONS.items():
        px, py = (sx - CHEMINEE[0]) / 1000, (sy - CHEMINEE[1]) / 1000
        ax.plot(px, py, "o", ms=8, mfc="w", mec="k", zorder=5)
        dx, dy, ha = DECALAGE[nom]
        ax.annotate(nom, (px, py), xytext=(dx, dy), textcoords="offset points", fontsize=9, ha=ha)
    ax.plot(0, 0, "^", ms=12, mfc="red", mec="k", zorder=6, ls="none", label=t("Cheminée O-I"))
    ax.legend(loc="upper right", fontsize=9)
    ax.set(xlim=etendue[:2], ylim=etendue[2:], xlabel=t("Est (km depuis la cheminée)"), ylabel=t("Nord (km)"),
           title=t("Relief IGN (RGE ALTI, 25 m) et domaine des récepteurs (20 × 20 km)"))
    fig.tight_layout()
    fig.savefig(PROJET / "figures" / fichier("relief_recepteurs.png"), dpi=140)
    print("Écrit : figures/" + fichier("relief_recepteurs.png"))
