"""Étape 8 — juillet 2024 : AERMOD avec la météo WRF (MMIF) et avec Prunay, options rurale et urbaine.

Même chaîne que janvier (scripts/aermod_wrf_janvier.py et _sensibilite.py), quatre météos :
  wrf             : surfaces de MMIF (maille bâtie, z0 0,80 m) ;
  prunay          : AERMET Prunay 2024 (surface autour du mât), limité à juillet ;
  wrf-surf_prunay : vent WRF, surface d'été de Prunay (albédo 0,19, Bowen 0,35, z0 0,15 m) ;
  wrf-z025        : vent WRF, z0 0,25 m autour de la cheminée (variante : la règle de l'EPA est la surface MMIF, cas « wrf »), même albédo
                    et Bowen.
Dossiers aermod/jul_<météo>_<option>/, moyenne PERIOD, STARTEND juillet.
"""
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from aermod_wrf_janvier import AERMOD, MODELES, PROJET, lancer

MMIF = PROJET / "wrf/mmif/juillet"
STARTEND = "   STARTEND  2024 07 01 01  2024 07 31 24"
SURFACES = {"surf_prunay": (0.19, 0.35, 0.15), "z025": (0.19, 0.35, 0.25)}


def bloc_me(sfc, pfl, surf, uair, profbase):
    return f"""ME STARTING
   SURFFILE  {sfc}
   PROFFILE  {pfl}
   SURFDATA  {surf}
   UAIRDATA  {uair}
   PROFBASE  {profbase}  METERS
{STARTEND}
ME FINISHED"""


def bloc_wrf(chemin, sfc="sfc", pfl="pfl"):
    return bloc_me(f"{chemin}.{sfc}", f"{chemin}.{pfl}", "99999  2024  WRF-MMIF", "99999  2024  WRF-MMIF", 104.7)


def aermet(nom, albedo, bowen, z0):
    dossier = MMIF / "variantes" / nom
    dossier.mkdir(parents=True, exist_ok=True)
    lignes = (MMIF / "OI_JUILLET.AERSFC.DAT").read_text().splitlines()
    lignes = [f"   SITE_CHAR    {l.split()[1]:>2s}       1     {albedo:.2f}     {bowen:.2f}   {z0:.5f}"
              if l.strip().startswith("SITE_CHAR") else l for l in lignes]
    (dossier / "aersfc.dat").write_text("\n".join(lignes) + "\n")
    t = (MMIF / "oi_juillet.IN1").read_text()
    for a, b in [("oi_juillet.ER1", "aermet.er1"), ("oi_juillet.OU1", "aermet.ou1"),
                 ("DATA     OI_JUILLET.DAT", "DATA     ../../OI_JUILLET.DAT"), ("OI_JUILLET.DAT.OQA", "prog.oqa"),
                 ("AERSURF  OI_JUILLET.AERSFC.DAT", "AERSURF  aersfc.dat"),
                 ("oi_juillet.SFC", "variante.sfc"), ("oi_juillet.PFL", "variante.pfl")]:
        assert a in t, a
        t = t.replace(a, b)
    (dossier / "aermet.inp").write_text(t)
    r = subprocess.run([str(Path.home() / "AERMOD/bin/aermet"), "aermet.inp"], cwd=dossier,
                       capture_output=True, text=True)
    assert "AERMET FINISHED SUCCESSFULLY" in r.stdout, f"AERMET {nom} a échoué"
    return f"../../wrf/mmif/juillet/variantes/{nom}/variante"


def preparer(meteo, option, bloc):
    source = PROJET / "aermod" / MODELES[option]
    dossier = PROJET / "aermod" / f"jul_{meteo}_{option}"
    dossier.mkdir(exist_ok=True)
    for f in source.glob("*.txt"):
        shutil.copy(f, dossier)
    shutil.copy(source / "stations.rou", dossier)
    for cas in ("stations", "grille"):
        t = (source / f"aermod_{cas}.inp").read_text(encoding="latin-1")
        t = re.sub(r"ME STARTING.*?ME FINISHED", bloc, t, flags=re.S)
        t = t.replace("AVERTIME  1  ANNUAL", "AVERTIME  1  PERIOD")
        t = re.sub(r"PLOTFILE  ANNUAL  ALL  annuel_", "PLOTFILE  PERIOD  ALL  periode_", t)
        t = re.sub(r"TITLEONE .*", f"TITLEONE  O-I Reims - NOx juillet 2024 - meteo {meteo} - {option} ({cas})", t)
        assert "STARTEND" in t and "PERIOD" in t
        (dossier / f"aermod_{cas}.inp").write_text(t, encoding="latin-1")
    return dossier


if __name__ == "__main__":
    assert AERMOD.exists()
    meteos = {
        "wrf": bloc_wrf("../../wrf/mmif/juillet/oi_juillet", "SFC", "PFL"),
        "prunay": bloc_me("../../aermet/prunay_2024.sfc", "../../aermet/prunay_2024.pfl",
                          "07072  2024  REIMS-PRUNAY", "00007145  2024  TRAPPES", 96.0),
    }
    for nom, valeurs in SURFACES.items():
        meteos[f"wrf-{nom}"] = bloc_wrf(aermet(nom, *valeurs))
    taches = [(preparer(m, o, b), c) for m, b in meteos.items() for o in MODELES for c in ("stations", "grille")]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for nom, cas, ok in pool.map(lancer, taches):
            print(f"{nom:28s} {cas:8s} {'OK' if ok else 'ÉCHEC'}", flush=True)
