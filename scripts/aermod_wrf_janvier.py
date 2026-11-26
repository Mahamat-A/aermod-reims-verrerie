"""Étape 8 — AERMOD en janvier 2024 avec la météo WRF (MMIF) et avec Prunay, options rurale et urbaine.

Crée aermod/jan_{wrf,prunay}_{rural,urbain}/ à partir de reference_bati (rural) et reference_urbaine (urbain) :
même source, mêmes bâtiments et récepteurs ; seule la météo change. Période limitée au mois de janvier
(STARTEND), moyenne « PERIOD » au lieu de « ANNUAL ». Lance les 8 calculs (stations + grille).
"""
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
AERMOD = Path.home() / "AERMOD/bin/aermod"
MODELES = {"rural": "reference_bati", "urbain": "reference_urbaine"}
METEO = {
    "wrf": """ME STARTING
   SURFFILE  ../../wrf/mmif/janvier/oi_janvier.SFC
   PROFFILE  ../../wrf/mmif/janvier/oi_janvier.PFL
   SURFDATA  99999  2024  WRF-MMIF
   UAIRDATA  99999  2024  WRF-MMIF
** Altitude du sol de la maille WRF de la cheminée (d03, 1 km)
   PROFBASE  104.7  METERS
   STARTEND  2024 01 01 01  2024 01 31 24
ME FINISHED""",
    "prunay": """ME STARTING
   SURFFILE  ../../aermet/prunay_2024.sfc
   PROFFILE  ../../aermet/prunay_2024.pfl
   SURFDATA  07072  2024  REIMS-PRUNAY
   UAIRDATA  00007145  2024  TRAPPES
** Altitude du sol à la station météo (Prunay)
   PROFBASE  96.0  METERS
   STARTEND  2024 01 01 01  2024 01 31 24
ME FINISHED""",
}


def preparer(meteo, option):
    source = PROJET / "aermod" / MODELES[option]
    dossier = PROJET / "aermod" / f"jan_{meteo}_{option}"
    dossier.mkdir(exist_ok=True)
    for f in source.glob("*.txt"):
        shutil.copy(f, dossier)
    shutil.copy(source / "stations.rou", dossier)
    for cas in ("stations", "grille"):
        t = (source / f"aermod_{cas}.inp").read_text(encoding="latin-1")
        t = re.sub(r"ME STARTING.*?ME FINISHED", METEO[meteo], t, flags=re.S)
        t = t.replace("AVERTIME  1  ANNUAL", "AVERTIME  1  PERIOD")
        t = re.sub(r"PLOTFILE  ANNUAL  ALL  annuel_", "PLOTFILE  PERIOD  ALL  periode_", t)
        t = re.sub(r"TITLEONE .*", f"TITLEONE  O-I Reims - NOx janvier 2024 - meteo {meteo} - {option} ({cas})", t)
        assert "STARTEND" in t and "PERIOD" in t
        (dossier / f"aermod_{cas}.inp").write_text(t, encoding="latin-1")
    return dossier


def lancer(args):
    dossier, cas = args
    r = subprocess.run([str(AERMOD), f"aermod_{cas}.inp", f"aermod_{cas}.out"], cwd=dossier,
                       capture_output=True, text=True)
    sortie = (dossier / f"aermod_{cas}.out").read_text(encoding="latin-1", errors="replace")
    ok = "*** AERMOD Finishes Successfully ***" in sortie or "Finishes Successfully" in r.stdout
    return dossier.name, cas, ok


if __name__ == "__main__":
    taches = [(preparer(m, o), c) for m in METEO for o in MODELES for c in ("stations", "grille")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for nom, cas, ok in pool.map(lancer, taches):
            print(f"{nom:20s} {cas:8s} {'OK' if ok else 'ÉCHEC — voir erreurs_' + cas + '.out'}")
