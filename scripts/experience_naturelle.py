"""Expérience naturelle 2013–2025 : le NO₂ mesuré par vent venant de l'usine suit-il les émissions d'O-I ?

Idée : les émissions annuelles de la verrerie ont varié d'un facteur 4 (143 à 566 t de NOx). Pour chaque
station et chaque année, on calcule D = NO₂ moyen par vent venant de l'usine (± 15°) − NO₂ moyen par vent
des secteurs voisins (15 à 45° de part et d'autre). Les secteurs voisins ont une météo proche mais ne
reçoivent pas le panache : la différence retire l'essentiel des effets communs (trafic, saison, stabilité).
Si l'usine contribue comme le prédit AERMOD, D doit augmenter avec les émissions avec la pente
k = D_modèle(2024) / 143 t. On estime β = pente observée / pente modélisée (β = 1 : modèle juste,
β = 0 : aucun effet visible), avec une tendance linéaire par station pour absorber les évolutions lentes.

Données : NO₂ horaire validé de l'AEE (e-reporting E1a, heures en UTC+1, ramenées en UTC), vent horaire
Météo-France de Reims-Prunay (51449002, 10 m, heure UTC de fin), émissions IREP, sorties horaires AERMOD
du cas de référence urbain 2024 (NOx, converti en NO₂ par 0,9 comme à l'étape 6).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from compare_secteurs import DIRECTION_USINE, cle_aermod, X_STATIONS

PROJET = Path(__file__).resolve().parent.parent
CODES = {"jean_daulan": "FR14012", "doumer": "FR14011", "betheny": "FR14010"}
NOMS = {"jean_daulan": "Jean d'Aulan (fond urbain)", "doumer": "Doumer (trafic)", "betheny": "Bétheny (périurbain)"}
# IREP, t/an de NOx (éq. NO₂) ; 2020 non déclarée (exclue)
EMISSIONS = {2013: 343, 2014: 343, 2015: 450, 2016: 566, 2017: 517, 2018: 437, 2019: 275,
             2021: 361, 2022: 384, 2023: 275, 2024: 143, 2025: 250}
DEMI_SECTEUR, VOISINS = 15, 45
VENT_MIN = 1.0          # m/s : en dessous, la direction n'a pas de sens
NO2_SUR_NOX = 0.9


def lire_no2():
    series = {}
    for s, code in CODES.items():
        d = pd.read_parquet(PROJET / f"donnees/eea_no2/SPO-{code}_8.parquet")
        d = d[(d["Validity"] > 0) & (d["Value"].astype(float) >= 0)]
        debut_utc = pd.to_datetime(d["Start"]) - pd.Timedelta(hours=1)     # AEE : UTC+1
        series[s] = pd.Series(d["Value"].astype(float).values, index=debut_utc)
    return pd.DataFrame(series)


def lire_vent():
    morceaux = []
    for f in ["H_51_2010-2019.csv.gz", "H_51_2020-2024.csv.gz", "H_51_latest-2025-2026.csv.gz"]:
        d = pd.read_csv(PROJET / "donnees/meteo_brute" / f, sep=";", usecols=["NUM_POSTE", "AAAAMMJJHH", "FF", "DD"],
                        dtype={"AAAAMMJJHH": str})
        morceaux.append(d[d["NUM_POSTE"] == 51449002])
    v = pd.concat(morceaux)
    v.index = pd.to_datetime(v["AAAAMMJJHH"], format="%Y%m%d%H")
    # une mesure qui commence à t (UTC) est associée au vent relevé à t + 1 h (fin de l'heure)
    v.index = v.index - pd.Timedelta(hours=1)
    return v[["FF", "DD"]].sort_index()[lambda x: ~x.index.duplicated()]


def secteur(direction, d_usine):
    ecart = ((direction - d_usine + 180) % 360) - 180
    return np.where(ecart.abs() <= DEMI_SECTEUR, "usine",
                    np.where((ecart.abs() > DEMI_SECTEUR) & (ecart.abs() <= VOISINS), "voisins", ""))


def ecart_secteurs(valeurs, direction, d_usine, n_tirages=300, graine=0):
    """D = moyenne(usine) − moyenne(voisins) et son écart type par rééchantillonnage de jours entiers."""
    t = pd.DataFrame({"v": valeurs, "s": secteur(direction, d_usine)}).dropna()
    t = t[t["s"] != ""]
    jours = t.index.normalize()
    par_jour = t.groupby([jours, "s"])["v"].agg(["sum", "count"]).unstack(fill_value=0)
    somme, nombre = par_jour["sum"], par_jour["count"]
    d = somme["usine"].sum() / nombre["usine"].sum() - somme["voisins"].sum() / nombre["voisins"].sum()
    rng = np.random.default_rng(graine)
    tirages = []
    for _ in range(n_tirages):
        i = rng.integers(0, len(par_jour), len(par_jour))
        su, nu, sv, nv = somme["usine"].values[i].sum(), nombre["usine"].values[i].sum(), \
            somme["voisins"].values[i].sum(), nombre["voisins"].values[i].sum()
        tirages.append(su / nu - sv / nv)
    return d, np.std(tirages), int(nombre["usine"].sum())


def pente_modele(vent, cas="reference_urbaine"):
    """k = D modélisé en 2024 (NO₂ de l'usine, µg/m³) / 143 t, avec le même vent et les mêmes secteurs."""
    lignes = [l.split() for l in (PROJET / f"aermod/{cas}/horaire_stations.pst").open() if not l.startswith("*")]
    m = pd.DataFrame({"station": [X_STATIONS[round(float(l[0]), 1)] for l in lignes],
                      "cle": [l[8] for l in lignes], "nox": [float(l[2]) for l in lignes]})
    m = m.pivot(index="cle", columns="station", values="nox") * NO2_SUR_NOX
    heures = pd.date_range("2024-01-01", "2024-12-31 23:00", freq="h")
    modele = m.reindex(cle_aermod(heures)).set_axis(heures)
    v = vent.reindex(heures)
    ok = v["FF"] >= VENT_MIN
    return {s: ecart_secteurs(modele[s][ok], v["DD"][ok], DIRECTION_USINE[s])[0] / EMISSIONS[2024]
            for s in DIRECTION_USINE}


def tableau(no2, vent):
    t = no2.join(vent, how="inner")
    t = t[t["FF"] >= VENT_MIN]
    lignes = []
    for s, d_usine in DIRECTION_USINE.items():
        for an, e in EMISSIONS.items():
            a = t[t.index.year == an]
            if a[s].notna().sum() < 4000:          # station fermée ou ouverte en cours d'année
                continue
            d, et, n = ecart_secteurs(a[s], a["DD"], d_usine, graine=an)
            lignes.append({"station": s, "annee": an, "emission_t": e, "D": d, "D_et": et, "heures_usine": n})
    return pd.DataFrame(lignes)


def ajuster(r, k):
    """Moindres carrés pondérés : D = a_s + b_s·(année − 2019) + β·k_s·E. Renvoie β et son écart type."""
    stations = list(r.station.unique())
    X, y, w = [], [], []
    for _, l in r.iterrows():
        ligne = []
        for s in stations:
            ligne += [1.0 if l.station == s else 0.0, (l.annee - 2019) if l.station == s else 0.0]
        ligne.append(k[l.station] * l.emission_t)
        X.append(ligne); y.append(l.D); w.append(1 / l.D_et ** 2)
    X, y, w = np.array(X), np.array(y), np.array(w)
    A = X * np.sqrt(w)[:, None]
    coef, *_ = np.linalg.lstsq(A, y * np.sqrt(w), rcond=None)
    residus = (y - X @ coef) * np.sqrt(w)
    chi2_red = residus @ residus / (len(y) - X.shape[1])
    cov = np.linalg.inv(A.T @ A) * max(1.0, chi2_red)      # erreurs gonflées si la dispersion dépasse le bruit
    return coef[-1], np.sqrt(cov[-1, -1]), chi2_red


CAS = {"reference_urbaine": ("option urbaine", "#1f5fa8"),
       "reference_bati": ("option rurale", "#d9822b")}


def k_bruite(vent, cas, sigma, n=5):
    """Pente modélisée quand la direction du vent utilisée pour trier les heures diffère de celle du
    panache (écart aléatoire d'écart type sigma) : c'est la situation des mesures, triées avec le vent
    de Prunay alors que le panache suit le vent local."""
    if sigma == 0:
        return pente_modele(vent, cas)
    ks = []
    for g in range(n):
        v = vent.copy()
        v["DD"] = (v["DD"] + np.random.default_rng(g).normal(0, sigma, len(v))) % 360
        ks.append(pente_modele(v, cas))
    return {s: float(np.mean([k[s] for k in ks])) for s in ks[0]}


def sans_tendance(d):
    """Retire la tendance linéaire de la station (ajustée avec un terme libre en émissions), pour
    montrer sur la figure ce que mesure β."""
    X = np.column_stack([np.ones(len(d)), d.annee - 2019, d.emission_t])
    w = 1 / d.D_et.values ** 2
    coef, *_ = np.linalg.lstsq(X * np.sqrt(w)[:, None], d.D.values * np.sqrt(w), rcond=None)
    return d.D - coef[1] * (d.annee - 2019)


def figure(r, pentes):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=True)
    for ax, s in zip(axes, DIRECTION_USINE):
        d = r[r.station == s]
        dc = sans_tendance(d)
        ax.errorbar(d.emission_t, dc, yerr=d.D_et, fmt="o", color="#4a4a4a", ms=5, capsize=2, lw=1,
                    label="mesures, corrigées de la tendance (± 1 écart type)" if s == "jean_daulan" else None)
        for (_, l), y in zip(d.iterrows(), dc):
            ax.annotate(str(l.annee)[2:], (l.emission_t, y), xytext=(4, 3), textcoords="offset points",
                        fontsize=7, color="#777777")
        e = np.linspace(100, 600, 2)
        for cas, (k, beta, beta_et) in pentes.items():
            nom, couleur = CAS[cas]
            centre = np.average(dc - k[s] * d.emission_t, weights=1 / d.D_et ** 2)
            ax.plot(e, centre + k[s] * e, color=couleur, lw=2,
                    label=f"pente prévue par AERMOD, {nom} — β mesuré = {beta:.2f} ± {beta_et:.2f}"
                    if s == "jean_daulan" else None)
        ax.set_title(NOMS[s], fontsize=10)
        ax.set_xlabel("Émissions de NOx d'O-I (t/an, IREP)")
        ax.axhline(0, color="#bbbbbb", lw=0.8)
    axes[0].set_ylabel("NO₂ : secteur usine − secteurs voisins (µg/m³)")
    fig.legend(loc="lower center", ncol=1, fontsize=8.5, frameon=False)
    fig.suptitle("Expérience naturelle 2013–2025 : le NO₂ par vent venant de l'usine suit-il ses émissions ? "
                 "(β = 1 : modèle juste ; β = 0 : aucun effet)", fontsize=10.5)
    fig.tight_layout(rect=(0, 0.17, 1, 1))
    sortie = PROJET / "figures/etape6_experience_naturelle.png"
    fig.savefig(sortie, dpi=150)
    return sortie


if __name__ == "__main__":
    no2, vent = lire_no2(), lire_vent()
    r = tableau(no2, vent)
    r.to_csv(PROJET / "observations/experience_naturelle.csv", index=False, float_format="%.3f")
    print(r.pivot(index="annee", columns="station", values="D").round(2).join(
        pd.Series(EMISSIONS, name="E_t")).to_string())
    print("\nécart type moyen de D :", r.groupby("station")["D_et"].mean().round(2).to_dict())
    print("heures « vent de l'usine » par an :", r.groupby("station")["heures_usine"].median().to_dict())
    pentes = {}
    for cas in CAS:
        for sigma in [0, 10, 20]:
            k = k_bruite(vent, cas, sigma)
            beta, beta_et, chi2 = ajuster(r, k)
            print(f"{cas:18s} écart de direction σ = {sigma:2d}° : k JdA/Doumer/Bétheny = "
                  + "/".join(f"{1000 * k[s]:.1f}" for s in DIRECTION_USINE)
                  + f" µg/m³ pour 1 000 t | β = {beta:+.2f} ± {beta_et:.2f} (χ² réduit {chi2:.2f}), "
                  f"β = 1 à {(1 - beta) / beta_et:.1f} σ")
            if sigma == 0:
                pentes[cas] = (k, beta, beta_et)
    print("figure :", figure(r, pentes))
