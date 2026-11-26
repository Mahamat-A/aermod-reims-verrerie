"""Luminosité et brouillard à Reims-Prunay en 2024 : ce qu'AERMET en voit, et l'effet sur AERMOD.

1. Rayonnement : AERMET n'a pas de mesure de rayonnement ; il l'estime à partir de la nébulosité (formule de
   Kasten-Czeplak, R = (990 sin φ − 30)(1 − 0,75 n^3,4)). On le compare au rayonnement global mesuré par Météo-France
   (GLO, poste 51449002), puis on écrit une variante du fichier AERMET étape 1 où, le jour (soleil > 10°), la
   nébulosité est celle qui redonne le rayonnement mesuré (aermet/rayonnement/, puis aermod/rayonnement_*).
2. Brouillard : heures à visibilité < 1 km (VV Météo-France) ; état de la couche limite selon AERMET, NOx mesuré et
   contribution modélisée de l'usine pendant ces heures et juste après la levée du brouillard le matin.
3. Fumigation (rabattement du panache au moment où l'inversion se dissipe), absente d'AERMOD : formule de Turner (1970)
   à des distances imposées (1–5 km). Estimation trop forte, gardée pour mémoire : AERSCREEN calcule la distance
   (9,3 km, panache déjà élargi) et donne 6,5 µg/m³ (aerscreen/rural_z025/) ; c'est la valeur retenue.
Temps : Météo-France en UTC, fin d'heure ; AERMET/AERMOD en heure locale d'hiver (UTC+1), fin d'heure.
"""
import re
import sys

import numpy as np
import pandas as pd

from compare_secteurs import X_STATIONS, cle_aermod
from aermod_wrf_janvier import PROJET

SORTIE = PROJET / "donnees/brouillard"
LAT, LON = 49.209, 4.155          # Prunay
STATIONS = ["jean_daulan", "doumer", "betheny"]


def meteo_france():
    mf = pd.read_csv(PROJET / "donnees/meteo_brute/H_51_2020-2024.csv.gz", sep=";", dtype=str,
                     usecols=["NUM_POSTE", "AAAAMMJJHH", "FF", "DD", "VV", "WW", "N", "INS", "GLO", "U", "T"])
    mf = mf[(mf.NUM_POSTE == "51449002") & mf.AAAAMMJJHH.str.startswith("2024")]
    mf.index = pd.to_datetime(mf.AAAAMMJJHH, format="%Y%m%d%H")
    return mf.drop(columns=["NUM_POSTE", "AAAAMMJJHH"]).apply(pd.to_numeric, errors="coerce")


def sin_hauteur_soleil(fin_utc):
    """Sinus de la hauteur du soleil au milieu de l'heure (formules de la NOAA)."""
    mid = fin_utc - pd.Timedelta(minutes=30)
    doy, hr = mid.dayofyear.values, mid.hour.values + mid.minute.values / 60
    g = 2 * np.pi / 365 * (doy - 1 + (hr - 12) / 24)
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g) - 0.006758 * np.cos(2 * g)
            + 0.000907 * np.sin(2 * g) - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    eqt = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g) - 0.014615 * np.cos(2 * g)
                    - 0.040849 * np.sin(2 * g))
    ha = np.radians((hr * 60 + eqt + 4 * LON) / 4 - 180)
    lat = np.radians(LAT)
    return np.sin(lat) * np.sin(decl) + np.cos(lat) * np.cos(decl) * np.cos(ha)


def qa_aermet():
    """Fichier AERMET étape 1 de Prunay ; index = clé AERMOD (aammjjhh, heure locale de fin)."""
    q = pd.read_csv(PROJET / "aermet/prunay_2024.oqa", sep=r"\s+", skiprows=4, dtype=str)
    q.index = q.DATE.str[2:] + q.HR
    tskc, asky = pd.to_numeric(q.TSKC), pd.to_numeric(q.ASKY)
    # nébulosité totale en dixièmes : TSKC (total × 100 + opaque), sinon ASKY
    return (tskc // 100).where((tskc < 9999) & (tskc // 100 <= 10)).fillna(asky.where(asky <= 10))


def rayonnement(mf):
    debut = mf.index - pd.Timedelta(hours=1)
    t = mf.assign(neb=qa_aermet().reindex(cle_aermod(debut)).values, sinphi=sin_hauteur_soleil(mf.index))
    t["R_clair"] = np.clip(990 * t.sinphi - 30, 0, None)
    t["R_aermet"] = t.R_clair * (1 - 0.75 * (t.neb / 10) ** 3.4)
    t["R_mes"] = t.GLO * 10000 / 3600                          # J/cm² par heure → W/m²
    d = t[(t.sinphi > 0.17) & t.R_aermet.notna() & t.R_mes.notna()]
    e = d.R_aermet - d.R_mes
    print(f"Rayonnement, {len(d)} heures de jour : AERMET {d.R_aermet.mean():.0f} W/m², mesuré {d.R_mes.mean():.0f}, "
          f"biais {100 * e.mean() / d.R_mes.mean():+.0f} %, r = {np.corrcoef(d.R_aermet, d.R_mes)[0, 1]:.2f}, "
          f"|écart| > 100 W/m² : {100 * (e.abs() > 100).mean():.0f} %")
    for nom, s in [("clair 0–2/10", d.neb <= 2), ("3–8/10", d.neb.between(3, 8)), ("couvert 9–10/10", d.neb >= 9)]:
        x = d[s]
        print(f"  {nom:16s} {len(x):5d} h : AERMET {x.R_aermet.mean():4.0f}, mesuré {x.R_mes.mean():4.0f} W/m², "
              f"soleil mesuré {x.INS.mean():4.1f} min/h")
    return t


def variante_rayonnement(t):
    """Réécrit le fichier AERMET étape 1 avec, le jour, la nébulosité qui redonne le rayonnement mesuré."""
    jour = (t.sinphi > 0.17) & t.R_mes.notna() & (t.R_clair > 0)
    n = (((1 - (t.R_mes / t.R_clair).clip(upper=1)) / 0.75) ** (1 / 3.4)).clip(0, 1).where(jour)
    dixiemes = (10 * n).round().dropna().astype(int)
    cle = dict(zip(cle_aermod(dixiemes.index - pd.Timedelta(hours=1)), dixiemes.values))

    def remplace(ligne, k, valeur):
        tok = list(re.finditer(r"\S+", ligne))
        return ligne[:tok[k - 1].end()] + valeur.rjust(tok[k].end() - tok[k - 1].end()) + ligne[tok[k].end():]

    lignes = (PROJET / "aermet/prunay_2024.oqa").read_text().split("\n")
    for i, l in enumerate(lignes):
        p = l.split()
        if len(p) > 8 and re.fullmatch(r"\d{8}", p[0]) and p[0][2:] + p[1] in cle:
            v = cle[p[0][2:] + p[1]]
            lignes[i] = remplace(remplace(l, 6, f"{v * 100 + 99:.1f}"), 8, f"{v:.1f}")
    (PROJET / "aermet/rayonnement/prunay_2024_ray.oqa").write_text("\n".join(lignes))
    print(f"Variante écrite : {len(cle)} heures de jour, nébulosité moyenne {t.neb[jour].mean():.1f} → {dixiemes.mean():.1f} dixièmes")


def brouillard(mf):
    debut = mf.index - pd.Timedelta(hours=1)
    cle = cle_aermod(debut)
    a = np.array([[float(v) for v in l.split()[:17]] for l in open(PROJET / "aermet/prunay_2024.sfc").readlines()[1:]])
    k = [f"{int(r[0]) % 100:02d}{int(r[1]):02d}{int(r[2]):02d}{int(r[4]):02d}" for r in a]
    sfc = pd.DataFrame({"H": a[:, 5], "ustar": a[:, 6], "zim": a[:, 10], "L": a[:, 11], "ws": a[:, 15]}, index=k)
    t = mf.set_axis(debut).assign(**sfc.reindex(cle).set_axis(debut), neb=qa_aermet().reindex(cle).values)
    obs = pd.read_csv(PROJET / "observations/reims_2024_horaire.csv", parse_dates=["debut_utc"], index_col=0)
    t = t.join(obs[[f"{s}_nox" for s in STATIONS]])
    for cas, nom in [("reference_bati", "rural"), ("reference_urbaine", "urbain")]:
        l = [x.split() for x in open(PROJET / f"aermod/{cas}/horaire_stations.pst") if not x.startswith("*")]
        m = pd.DataFrame({"s": [X_STATIONS[round(float(x[0]), 1)] for x in l], "cle": [x[8] for x in l],
                          "c": [float(x[2]) for x in l]}).pivot(index="cle", columns="s", values="c")
        for s in STATIONS:
            t[f"{nom}_{s}"] = m[s].reindex(cle).values
    t["brouillard"] = t.VV < 1000
    t.to_csv(SORTIE / "heures_brouillard_2024.csv")
    b, r = t[t.brouillard], t[~t.brouillard]
    print(f"\nBrouillard (VV < 1 km) : {len(b)} h ; par mois {b.index.month.value_counts().sort_index().to_dict()}")
    print("  AERMET, médianes brouillard / reste : " + " ; ".join(
        f"{c} {b[c].median():.2f} / {r[c].median():.2f}" for c in ["ustar", "ws", "zim", "L"]))
    print(f"  heures stables : {(b.L > 0).mean():.0%} / {(r.L > 0).mean():.0%} ; "
          f"ciel clair pour AERMET pendant le brouillard : {(b.neb == 0).mean():.0%}")
    fin = t.brouillard.shift(1, fill_value=False) & ~t.brouillard
    apres = (fin | fin.shift(1, fill_value=False) | fin.shift(2, fill_value=False)) \
        & (t.index + pd.Timedelta(hours=1)).hour.isin(range(7, 14))
    x, y = t[apres], t[~t.brouillard & ~apres]
    print(f"  {int(fin.sum())} épisodes ; {int(apres.sum())} h dans les 3 h suivant une levée en matinée")
    print("  NOx (µg/m³)   mesuré brouillard / levée / reste | usine rural idem | usine urbain idem")
    for s in STATIONS:
        print(f"  {s:12s} " + " | ".join(" / ".join(f"{z[c].mean():.3f}" if c != f"{s}_nox" else f"{z[c].mean():.1f}"
                                                 for z in (b, x, y)) for c in (f"{s}_nox", f"rural_{s}", f"urbain_{s}")))


def fumigation():
    """Turner (1970) : plume stable (classe F, dθ/dz = 0,035 K/m) rabattue quand la couche mélangée l'atteint."""
    g, ta, ts, vs, d, hs = 9.81, 278.0, 523.0, 8.0, 2.51, 59.0
    q = 143e6 / (365.25 * 86400)                                  # g/s de NOx (143 t en 2024)
    fb = g * vs * d ** 2 / 4 * (ts - ta) / ts                     # flux de flottabilité (m⁴/s³)
    for u in (2.0, 3.0):
        s = g / ta * 0.035
        he = hs + 2.6 * (fb / (u * s)) ** (1 / 3)                 # Briggs, stable
        for x, sy, sz in ((1000, 40.0, 14.0), (3000, 100.0, 27.0), (5000, 150.0, 34.0)):   # Pasquill-Gifford F
            hi = he + 2 * sz
            c = q / (np.sqrt(2 * np.pi) * u * (sy + he / 8) * hi) * 1e6
            print(f"  u = {u:.0f} m/s, x = {x / 1000:.0f} km : He = {he:.0f} m, h_i = {hi:.0f} m → {c:.0f} µg/m³ NOx")


if __name__ == "__main__":
    SORTIE.mkdir(exist_ok=True)
    mf = meteo_france()
    t = rayonnement(mf)
    if "--variante" in sys.argv:
        variante_rayonnement(t)
    brouillard(mf)
    print("\nFumigation, Turner à distance imposée (surestimation ; valeur retenue : AERSCREEN, 6,5 µg/m³ à 9,3 km) :")
    fumigation()
