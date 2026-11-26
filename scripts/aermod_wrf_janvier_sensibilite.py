"""Étape 8 — sensibilité de l'AERMOD-WRF de janvier aux paramètres de surface et au mode MMIF.

Le vent, la température et la nébulosité restent ceux de WRF ; seuls changent :
  surf_prunay : albédo 0,19, Bowen 0,45, z0 0,03 m (valeurs d'hiver de Prunay) ;
  bowen       : albédo 0,19, Bowen 0,45, z0 0,80 m (rugosité WRF conservée) ;
  direct      : mode MMIF « AERMOD direct » (couche limite de WRF, sans AERMET).
Chaque variante est calculée en options rurale et urbaine (aermod/jan_wrf-<variante>_<option>/).
"""
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import aermod_wrf_janvier as base

MMIF = base.PROJET / "wrf/mmif/janvier"
SURFACES = {"surf_prunay": (0.19, 0.45, 0.03), "bowen": (0.19, 0.45, 0.80)}


def aermet(nom, albedo, bowen, z0):
    dossier = MMIF / "variantes" / nom
    dossier.mkdir(parents=True, exist_ok=True)
    lignes = (MMIF / "OI_JANVIER.AERSFC.DAT").read_text().splitlines()
    lignes = [f"   SITE_CHAR    {l.split()[1]:>2s}       1     {albedo:.2f}     {bowen:.2f}   {z0:.5f}"
              if l.strip().startswith("SITE_CHAR") else l for l in lignes]
    (dossier / "aersfc.dat").write_text("\n".join(lignes) + "\n")
    t = (MMIF / "oi_janvier.IN1").read_text()
    for a, b in [("oi_janvier.ER1", "aermet.er1"), ("oi_janvier.OU1", "aermet.ou1"),
                 ("DATA     OI_JANVIER.DAT", "DATA     ../../OI_JANVIER.DAT"), ("OI_JANVIER.DAT.OQA", "prog.oqa"),
                 ("AERSURF  OI_JANVIER.AERSFC.DAT", "AERSURF  aersfc.dat"),
                 ("oi_janvier.SFC", "variante.sfc"), ("oi_janvier.PFL", "variante.pfl")]:
        assert a in t, a
        t = t.replace(a, b)
    (dossier / "aermet.inp").write_text(t)
    r = subprocess.run([str(Path.home() / "AERMOD/bin/aermet"), "aermet.inp"], cwd=dossier,
                       capture_output=True, text=True)
    assert "AERMET FINISHED SUCCESSFULLY" in r.stdout, f"AERMET {nom} a échoué"
    return f"../../wrf/mmif/janvier/variantes/{nom}/variante"


def bloc_me(chemin):
    return f"""ME STARTING
   SURFFILE  {chemin}.sfc
   PROFFILE  {chemin}.pfl
   SURFDATA  99999  2024  WRF-MMIF
   UAIRDATA  99999  2024  WRF-MMIF
   PROFBASE  104.7  METERS
   STARTEND  2024 01 01 01  2024 01 31 24
ME FINISHED"""


if __name__ == "__main__":
    for nom, valeurs in SURFACES.items():
        base.METEO[f"wrf-{nom}"] = bloc_me(aermet(nom, *valeurs))
    base.METEO["wrf-direct"] = bloc_me("../../wrf/mmif/janvier/oi_janvier_direct")
    variantes = [m for m in base.METEO if m.startswith("wrf-")]
    taches = [(base.preparer(m, o), c) for m in variantes for o in base.MODELES for c in ("stations", "grille")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for nom, cas, ok in pool.map(base.lancer, taches):
            print(f"{nom:28s} {cas:8s} {'OK' if ok else 'ÉCHEC'}")
