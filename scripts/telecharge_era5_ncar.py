"""ERA5 pour forcer WRF sur Reims, depuis l'archive du NCAR (jeu d633000) au lieu du CDS Copernicus.

Pourquoi : le 22/11/2026, la file ERA5 du CDS était saturée (100 requêtes en cours, plus de 2 800 en attente).
L'archive NCAR contient les mêmes données ERA5 en netCDF (un fichier mondial par variable et par jour ou par mois).
Son serveur THREDDS découpe côté serveur (NetCDF Subset Service) : on ne télécharge que la zone 43–55° N,
5° O–13° E toutes les 3 heures, soit ≈ 4 Mo par variable et par jour au lieu de 1,3 Go.
Les fichiers gardent les noms NCAR, attendus par le convertisseur era5_to_int (format intermédiaire WPS).
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
import re
import time
import urllib.request

import netCDF4

TDS = "https://thredds.rda.ucar.edu/thredds"
ZONE = "north=55&south=43&west=-5&east=13"
PERIODES = {"janvier": (date(2023, 12, 28), date(2024, 2, 1)), "juillet": (date(2024, 6, 28), date(2024, 8, 1))}
SORTIE = Path(__file__).resolve().parent.parent / "wrf" / "era5_ncar"

# code ECMWF du fichier NCAR -> nom de la variable dans le fichier
NIVEAUX_PRESSION = {"128_129_z": "Z", "128_133_q": "Q", "128_130_t": "T", "128_131_u": "U", "128_132_v": "V"}
SURFACE = {"128_034_sstk": "SSTK", "128_235_skt": "SKT", "128_039_swvl1": "SWVL1", "128_040_swvl2": "SWVL2",
           "128_041_swvl3": "SWVL3", "128_042_swvl4": "SWVL4", "128_139_stl1": "STL1", "128_170_stl2": "STL2",
           "128_183_stl3": "STL3", "128_236_stl4": "STL4", "128_031_ci": "CI", "128_167_2t": "VAR_2T",
           "128_168_2d": "VAR_2D", "128_165_10u": "VAR_10U", "128_166_10v": "VAR_10V", "128_033_rsn": "RSN",
           "128_141_sd": "SD", "128_151_msl": "MSL", "128_134_sp": "SP"}
INVARIANTS = {"128_172_lsm": "LSM", "128_129_z": "Z"}


def catalogue(dossier):
    """Noms des fichiers d'un dossier du catalogue THREDDS."""
    for essai in range(1, 6):
        try:
            xml = urllib.request.urlopen(f"{TDS}/catalog/files/d633000/{dossier}/catalog.xml", timeout=120).read()
            return re.findall(r'name="(e5\.[^"]+\.nc)"', xml.decode())
        except Exception as e:
            # le serveur coupe parfois les longues réponses : on recommence
            print(f"catalogue {dossier}, essai {essai} raté : {e}", flush=True)
            time.sleep(10 * essai)
    raise RuntimeError(f"catalogue {dossier} illisible")


def taches():
    """Liste (chemin THREDDS, variable, début, fin, nombre d'heures attendu).
    Ordre : invariants, surface (fichiers mensuels, légers), puis niveaux de pression jour par jour,
    pour pouvoir tester la conversion WPS dès les premiers jours reçus."""
    liste = []
    mois_vus = {}
    for debut, fin in PERIODES.values():
        jours = [debut + timedelta(n) for n in range((fin - debut).days + 1)]
        for j in jours:
            m = f"{j:%Y%m}"
            if m not in mois_vus:
                mois_vus[m] = (catalogue(f"e5.oper.an.pl/{m}"), catalogue(f"e5.oper.an.sfc/{m}"), [])
            mois_vus[m][2].append(j)
            for code, var in NIVEAUX_PRESSION.items():
                nom = next(f for f in mois_vus[m][0] if f".{code}." in f and f".{j:%Y%m%d}00_" in f)
                liste.append((f"e5.oper.an.pl/{m}/{nom}", var, f"{j}T00:00:00Z", f"{j}T21:00:00Z", 8))
    for m, (_, fichiers_sfc, jours) in mois_vus.items():
        for code, var in SURFACE.items():
            nom = next(f for f in fichiers_sfc if f".{code}." in f)
            liste.append((f"e5.oper.an.sfc/{m}/{nom}", var, f"{min(jours)}T00:00:00Z", f"{max(jours)}T21:00:00Z",
                          8 * len(jours)))
    invariants = [(f"e5.oper.invariant/197901/e5.oper.invariant.{code}.ll025sc.1979010100_1979010100.nc", var,
                   "1979-01-01T00:00:00Z", "1979-01-01T00:00:00Z", 1) for code, var in INVARIANTS.items()]
    surface = [t for t in liste if "an.sfc" in t[0]]
    pression = [t for t in liste if "an.pl" in t[0]]
    return invariants + surface + pression


def telecharge(tache):
    chemin, var, debut, fin, n_attendu = tache
    cible = SORTIE / Path(chemin).name
    if cible.exists():
        return f"déjà là  {cible.name}"
    url = (f"{TDS}/ncss/grid/files/d633000/{chemin}?var={var}&{ZONE}"
           f"&time_start={debut}&time_end={fin}&timeStride=3&accept=netcdf")
    partiel = cible.with_suffix(".part")
    for essai in range(1, 6):
        try:
            with urllib.request.urlopen(url, timeout=900) as r, open(partiel, "wb") as f:
                f.write(r.read())
            with netCDF4.Dataset(partiel) as d:
                n = d.dimensions["time"].size
                forme = d.variables[var].shape
            if n != n_attendu:
                raise ValueError(f"{n} heures au lieu de {n_attendu}")
            partiel.rename(cible)
            return f"ok {forme}  {cible.name}"
        except Exception as e:
            print(f"essai {essai} raté pour {cible.name} : {e}", flush=True)
            time.sleep(30 * essai)
    return f"ÉCHEC  {cible.name}"


if __name__ == "__main__":
    SORTIE.mkdir(parents=True, exist_ok=True)
    liste = taches()
    print(f"{len(liste)} fichiers à obtenir", flush=True)
    debut = time.time()
    # 4 requêtes simultanées : assez pour avancer, sans surcharger le serveur du NCAR
    with ThreadPoolExecutor(4) as pool:
        for i, msg in enumerate(pool.map(telecharge, liste), 1):
            print(f"[{i}/{len(liste)}] {time.time() - debut:6.0f} s  {msg}", flush=True)
