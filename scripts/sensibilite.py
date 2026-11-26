"""Étape 7 : tests de sensibilité AERMOD (un paramètre à la fois) autour du cas de référence.

Chaque variante est une copie de aermod/reference_bati avec une seule modification ; les
calculs tournent en parallèle dans aermod/sensibilite/<variante>/.
Débit volumique réel conservé (39,7 m³/s) : si T ou D change, la vitesse est recalculée.
"""

import math
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
REF = PROJET / "aermod" / "reference_bati"
SENS = PROJET / "aermod" / "sensibilite"
AERMOD = Path.home() / "AERMOD" / "bin" / "aermod"
SRCPARAM_REF = "   SRCPARAM  CHEM1  6.0384  59.0  523.0  8.0  2.51"
Q_REF = 8.0 * math.pi * 2.51 ** 2 / 4           # m³/s réels à 523 K


def srcparam(ts=523.0, d=2.51):
    v = Q_REF * ts / 523.0 / (math.pi * d ** 2 / 4)
    return f"   SRCPARAM  CHEM1  6.0384  59.0  {ts:.1f}  {v:.2f}  {d:.2f}"


def heures_juillet_exact():
    """HOUREMIS : 2 fours jusqu'au 11/07 inclus (heure locale), four 2 seul ensuite."""
    lignes = [l.split() for l in list((PROJET / "aermet/prunay_2024.sfc").open())[1:]]
    out = []
    for l in lignes:
        an, mois, jour, heure = int(l[0]), int(l[1]), int(l[2]), int(l[4])
        q = 6.0384 if (mois, jour) <= (7, 11) else 2.8305
        out.append(f"SO HOUREMIS {an % 100:02d} {mois:2d} {jour:2d} {heure:2d} CHEM1 {q:.4f} 523.0 8.00")
    return "\n".join(out) + "\n"


def sillage_b():
    texte = (PROJET / "aermod/batiments/bpip.out").read_text().splitlines()
    return "\n".join(l.replace("CHEM1B", "CHEM1 ").replace(" SO ", "    ", 1).strip().join(["   ", ""])
                     for l in texte if " CHEM1B " in l and l.strip().startswith("SO "))


VARIANTES = {
    "position_B": [("LOCATION  CHEM1  POINT  576601.2  5453845.2  86.17",
                    "LOCATION  CHEM1  POINT  576566.2  5453873.1  86.47"),
                   ("INCLUDED  sillage_chem1.txt", "INCLUDED  sillage_chem1b.txt")],
    "diametre_1.5m": [(SRCPARAM_REF, srcparam(d=1.5))],
    "temperature_473K": [(SRCPARAM_REF, srcparam(ts=473.0))],
    "temperature_573K": [(SRCPARAM_REF, srcparam(ts=573.0))],
    "sans_batiments": [("   INCLUDED  sillage_chem1.txt\n", "")],
    "urbain_182000": [("   POLLUTID  NOX", "   POLLUTID  NOX\n   URBANOPT  182000  Reims"),
                      ("   SRCGROUP  ALL", "   URBANSRC  CHEM1\n   SRCGROUP  ALL")],
    "juillet_horaire": [("   EMISFACT  CHEM1  MONTH  1.0 1.0 1.0 1.0 1.0 1.0 0.65726 0.46875 0.46875 0.46875 0.46875 0.46875",
                         "   HOUREMIS  emissions_horaires.txt  CHEM1")],
}


def preparer(nom, remplacements):
    dossier = SENS / nom
    dossier.mkdir(parents=True, exist_ok=True)
    for f in ("sillage_chem1.txt", "stations.rou"):
        shutil.copy(REF / f, dossier / f)
    if nom == "position_B":
        (dossier / "sillage_chem1b.txt").write_text(sillage_b() + "\n")
    if nom == "juillet_horaire":
        (dossier / "emissions_horaires.txt").write_text(heures_juillet_exact())
    for cas in ("grille", "stations"):
        texte = (REF / f"aermod_{cas}.inp").read_text()
        for avant, apres in remplacements:
            if avant not in texte:
                raise ValueError(f"{nom} : motif absent de aermod_{cas}.inp : {avant!r}")
            texte = texte.replace(avant, apres)
        texte = texte.replace("cas de reference + batiments", f"sensibilite {nom}")
        texte = texte.replace("../../aermet/", "../../../aermet/").replace("../../aermap/", "../../../aermap/")
        (dossier / f"aermod_{cas}.inp").write_text(texte)
    return dossier


def lancer(args):
    dossier, cas = args
    subprocess.run([str(AERMOD), f"aermod_{cas}.inp", f"aermod_{cas}.out"], cwd=dossier,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    fatal = [l for l in (dossier / f"aermod_{cas}.out").read_text(errors="replace").splitlines()
             if "Fatal Error Message" in l]
    return dossier.name, cas, fatal[0].strip() if fatal else "sortie absente"


if __name__ == "__main__":
    dossiers = [preparer(n, r) for n, r in VARIANTES.items()]
    taches = [(d, c) for d in dossiers for c in ("stations", "grille")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for nom, cas, bilan in pool.map(lancer, taches):
            print(f"{nom:18s} {cas:8s} {bilan}")
