"""Faisabilité d'une campagne de tubes passifs sous le panache de la verrerie O-I.

Récepteurs virtuels à 0,5 ; 0,75 ; 1 ; 1,5 et 2 km de la cheminée, au nord-est (sous les vents dominants de
sud-ouest) et au sud-ouest (témoins au vent). Altitudes et hauteurs de colline reprises de la grille AERMAP
(récepteur de grille le plus proche, pas de 250 m). AERMOD horaire 2024 (options rural z0 0,25 et urbain), puis
moyennes sur 14 jours (durée d'exposition d'un tube), NO₂ = 0,9 × NOx comme dans le reste du projet.
"""
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

PROJET = Path(__file__).resolve().parent.parent
X0, Y0 = 576601.2, 5453845.2
DISTANCES = [500, 750, 1000, 1500, 2000]
AZIMUTS = {"NE": 45, "SO": 225}
CAS = {"rural_z025": "reference_bati_z025", "urbain": "reference_urbaine"}


def grille_aermap():
    txt = (PROJET / "aermap/recepteurs.rou").read_text()
    x0, nx, dx, y0, ny, dy = re.search(r"XYINC\s+(\S+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\S+)", txt).groups()
    nx, ny = int(nx), int(ny)
    champs = {"ELEV": {}, "HILL": {}}
    for nom, ligne, vals in re.findall(r"GRIDCART\s+GRILLE\s+(ELEV|HILL)\s+(\d+)\s+([\d.\s]+?)(?=\n\s*(?:GRIDCART|\*\*|RE|$))", txt):
        champs[nom].setdefault(int(ligne), []).extend(float(v) for v in vals.split())
    elev = np.array([champs["ELEV"][j] for j in range(1, ny + 1)])
    hill = np.array([champs["HILL"][j] for j in range(1, ny + 1)])
    assert elev.shape == (ny, nx), elev.shape
    return float(x0), float(dx), float(y0), float(dy), elev, hill


def recepteurs():
    x0, dx, y0, dy, elev, hill = grille_aermap()
    lignes, noms = [], []
    for nom, az in AZIMUTS.items():
        for d in DISTANCES:
            x = X0 + d * np.sin(np.radians(az)); y = Y0 + d * np.cos(np.radians(az))
            i, j = round((x - x0) / dx), round((y - y0) / dy)
            lignes.append(f"   DISCCART  {x:11.2f}  {y:11.2f}  {elev[j, i]:8.2f}  {hill[j, i]:8.2f}")
            noms.append(f"{nom}_{d}")
    return lignes, noms


if __name__ == "__main__":
    lignes, noms = recepteurs()
    resultats = {}
    for cas, modele in CAS.items():
        dossier = PROJET / "aermod" / f"tubes_{cas}"
        dossier.mkdir(exist_ok=True)
        for f in (PROJET / "aermod" / modele).glob("*.txt"):
            shutil.copy(f, dossier)
        (dossier / "tubes.rou").write_text("\n".join(lignes) + "\n")
        t = (PROJET / "aermod" / modele / "aermod_stations.inp").read_text(encoding="latin-1")
        t = t.replace("INCLUDED  stations.rou", "INCLUDED  tubes.rou").replace("horaire_stations.pst", "horaire_tubes.pst")
        t = t.replace("annuel_stations.plt", "annuel_tubes.plt").replace("erreurs_stations.out", "erreurs_tubes.out")
        (dossier / "aermod_tubes.inp").write_text(t, encoding="latin-1")
        subprocess.run([str(Path.home() / "AERMOD/bin/aermod"), "aermod_tubes.inp", "aermod_tubes.out"],
                       cwd=dossier, capture_output=True)
        assert "Finishes Successfully" in (dossier / "aermod_tubes.out").read_text(encoding="latin-1", errors="replace")
        brut = [l.split() for l in (dossier / "horaire_tubes.pst").open() if not l.startswith("*")]
        conc = np.array([float(l[2]) for l in brut]).reshape(-1, len(noms)) * 0.9
        heures = pd.date_range("2024-01-01 01:00", periods=conc.shape[0], freq="h")
        df = pd.DataFrame(conc, index=heures, columns=noms)
        resultats[cas] = df.resample("14D").mean()
    for cas, q in resultats.items():
        print(f"\n{cas} — NO₂ de l'usine en moyennes de 14 jours (µg/m³) : médiane / 90e centile / max")
        for d in DISTANCES:
            ne, so = q[f"NE_{d}"], q[f"SO_{d}"]
            diff = ne - so
            print(f"  {d:5d} m  NE {ne.median():.2f} / {ne.quantile(.9):.2f} / {ne.max():.2f} | SO {so.median():.2f} / "
                  f"{so.max():.2f} | NE − SO médiane {diff.median():+.2f}, moyenne annuelle {diff.mean():+.2f}")
