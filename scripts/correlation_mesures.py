"""Étape 8 — le NOx mesuré suit-il, heure par heure, la contribution de l'usine calculée par AERMOD ?

Pour chaque mois (janvier, juillet), chaque cas AERMOD et chaque station : régression
    NOx mesuré = β × NOx de l'usine modélisé + effets « heure du jour » + effets « classe de vent » + constante.
Si le modèle est juste, β ≈ 1 (le NOx mesuré contient l'apport de l'usine). Les effets heure du jour et vent absorbent
le trafic et la stabilité de l'air, qui font monter à la fois le NOx urbain et, parfois, le panache. L'incertitude
de β vient d'un rééchantillonnage de jours entiers (les heures d'un même jour ne sont pas indépendantes).
On donne aussi la corrélation de rang brute (Spearman), sans contrôle, pour montrer l'effet de la météo commune.
Vent des classes : WRF à la maille de l'usine (même vent pour tous les cas). Mesures : NOx validés ATMO (UTC).
"""
import numpy as np
import pandas as pd

from compare_secteurs import X_STATIONS, cle_aermod
from aermod_wrf_janvier import PROJET

MOIS = {"jan": (1, "wrf/mmif/janvier/oi_janvier.SFC"), "jul": (7, "wrf/mmif/juillet/oi_juillet.SFC")}
CAS = ["prunay_rural", "prunay_urbain", "wrf_rural", "wrf-z025_rural", "wrf-z025_urbain", "wrf-z0_1_rural",
       "wrf-z0_2_rural"]
STATIONS = ["jean_daulan", "doumer", "betheny"]
CLASSES_VENT = [0, 2, 3, 4, 6, 99]          # m/s


def modele(dossier, heures):
    lignes = [l.split() for l in (dossier / "horaire_stations.pst").open() if not l.startswith("*")]
    m = pd.DataFrame({"station": [X_STATIONS[round(float(l[0]), 1)] for l in lignes],
                      "cle": [l[8] for l in lignes], "nox": [float(l[2]) for l in lignes]})
    m = m.pivot(index="cle", columns="station", values="nox")
    return m.reindex(cle_aermod(heures)).set_axis(heures)


def vent_wrf(fichier, heures):
    a = np.array([[float(v) for v in l.split()[:17]] for l in open(fichier).readlines()[1:]])
    cle = [f"{int(r[0]) % 100:02d}{int(r[1]):02d}{int(r[2]):02d}{int(r[4]):02d}" for r in a]
    return pd.Series(a[:, 15], index=cle).reindex(cle_aermod(heures)).set_axis(heures)


def regression(y, x, heure, classe, jours, n_tirages=500, graine=0):
    controles = pd.get_dummies(pd.DataFrame({"h": heure, "v": classe}).astype(str), drop_first=True).astype(float)
    X = np.column_stack([x, np.ones(len(x)), controles.values])
    beta = np.linalg.lstsq(X, y, rcond=None)[0][0]
    rng = np.random.default_rng(graine)
    uniques = np.unique(jours)
    groupes = {j: np.flatnonzero(jours == j) for j in uniques}
    tirages = []
    for _ in range(n_tirages):
        i = np.concatenate([groupes[j] for j in rng.choice(uniques, len(uniques))])
        tirages.append(np.linalg.lstsq(X[i], y[i], rcond=None)[0][0])
    return beta, np.std(tirages)


if __name__ == "__main__":
    obs = pd.read_csv(PROJET / "observations/reims_2024_horaire.csv", parse_dates=["debut_utc"], index_col=0)
    lignes = []
    for mois, (num, sfc) in MOIS.items():
        heures = obs.index[obs.index.month == num]
        ws = vent_wrf(PROJET / sfc, heures)
        for cas in CAS:
            m = modele(PROJET / "aermod" / f"{mois}_{cas}", heures)
            for s in STATIONS:
                t = pd.DataFrame({"y": obs.loc[heures, f"{s}_nox"], "x": m[s], "ws": ws}).dropna()
                classe = pd.cut(t.ws, CLASSES_VENT, labels=False)
                b, e = regression(t.y.values, t.x.values, t.index.hour.values, classe.values,
                                  t.index.normalize().values)
                lignes.append({"mois": mois, "cas": cas, "station": s, "heures": len(t),
                               "modele_moy": t.x.mean(), "modele_P99": t.x.quantile(0.99),
                               "spearman_brut": t.x.corr(t.y, method="spearman"), "beta": b, "beta_et": e})
    r = pd.DataFrame(lignes)
    r["ecart_a_1_en_et"] = (r.beta - 1) / r.beta_et
    pd.set_option("display.width", 200)
    print(r.round(3).to_string(index=False))
    r.to_csv(PROJET / "rapport/etape8_correlation_mesures.csv", index=False, float_format="%.4f")
