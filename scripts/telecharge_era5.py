"""ERA5 (Copernicus CDS) pour forcer WRF sur Reims : janvier et juillet 2024, avec 3 jours de mise en route.

Niveaux de pression et surface, toutes les 3 h, GRIB (lu par ungrib, Vtable.ECMWF),
zone 43–55° N, 5° O–13° E. Requêtes découpées en tranches de 9 jours (limite de taille du CDS), une file par jeu de données (pression, surface) en parallèle,
puis concaténées (un fichier GRIB peut être mis bout à bout).
"""

import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import cdsapi

SORTIE = Path(__file__).resolve().parent.parent / "wrf" / "era5"
ZONE = [55, -5, 43, 13]   # N, O, S, E : couvre le domaine d01 (45–53° N, −2,5–10,7° E) avec marge
HEURES = [f"{h:02d}:00" for h in range(0, 24, 3)]
PERIODES = {"janvier": (date(2023, 12, 28), date(2024, 2, 1)), "juillet": (date(2024, 6, 28), date(2024, 8, 1))}
TRANCHE = 9
NIVEAUX = ["1", "2", "3", "5", "7", "10", "20", "30", "50", "70", "100", "125", "150", "175", "200",
           "225", "250", "300", "350", "400", "450", "500", "550", "600", "650", "700", "750", "775",
           "800", "825", "850", "875", "900", "925", "950", "975", "1000"]
PRESSION = ["geopotential", "temperature", "u_component_of_wind", "v_component_of_wind",
            "relative_humidity", "specific_humidity"]
SURFACE = ["10m_u_component_of_wind", "10m_v_component_of_wind", "2m_temperature",
           "2m_dewpoint_temperature", "surface_pressure", "mean_sea_level_pressure",
           "skin_temperature", "sea_surface_temperature", "sea_ice_cover", "land_sea_mask",
           "geopotential", "snow_depth", "soil_temperature_level_1", "soil_temperature_level_2",
           "soil_temperature_level_3", "soil_temperature_level_4", "volumetric_soil_water_layer_1",
           "volumetric_soil_water_layer_2", "volumetric_soil_water_layer_3", "volumetric_soil_water_layer_4"]

def tranches(debut, fin):
    while debut <= fin:
        bout = min(debut + timedelta(days=TRANCHE - 1), fin)
        yield debut, bout
        debut = bout + timedelta(days=1)


def telecharger(tache):
    """Une requête CDS (une tranche) ; chaque fil a son propre client."""
    jeu, variables, extra, debut, bout, morceau = tache
    if morceau.exists() and morceau.stat().st_size > 0:
        return f"déjà présent : {morceau.name}"
    requete = {"product_type": ["reanalysis"], "variable": variables,
               "date": f"{debut:%Y-%m-%d}/{bout:%Y-%m-%d}", "time": HEURES,
               "area": ZONE, "data_format": "grib", **extra}
    for essai in range(20):
        try:
            cdsapi.Client(quiet=True).retrieve(jeu, requete, str(morceau))
            return f"reçu : {morceau.name} ({morceau.stat().st_size / 1e6:.0f} Mo)"
        except Exception as erreur:          # file pleine côté CDS : on réessaie plus tard
            if "queued requests" not in str(erreur) or essai == 19:
                raise
            time.sleep(120)


def file_du_jeu(taches):
    """Les requêtes d'un même jeu de données, l'une après l'autre (règle du CDS)."""
    messages = []
    for tache in taches:
        messages.append(telecharger(tache))
        print(messages[-1], flush=True)
    return messages


if __name__ == "__main__":
    cibles, taches = {}, []
    for nom, (debut, fin) in PERIODES.items():
        for jeu, variables, extra in [("reanalysis-era5-pressure-levels", PRESSION, {"pressure_level": NIVEAUX}),
                                      ("reanalysis-era5-single-levels", SURFACE, {})]:
            cible = SORTIE / f"era5_{nom}_{'pl' if 'pressure' in jeu else 'sfc'}.grib"
            cibles[cible] = []
            for d, b in tranches(debut, fin):
                morceau = cible.with_suffix(f".{d:%Y%m%d}.part")
                cibles[cible].append(morceau)
                taches.append((jeu, variables, extra, d, b, morceau))
    # Le CDS limite les requêtes en file par jeu de données : une file par jeu (pression, surface),
    # les deux jeux en parallèle.
    par_jeu = {}
    for tache in taches:
        par_jeu.setdefault(tache[0], []).append(tache)
    with ThreadPoolExecutor(max_workers=len(par_jeu)) as pool:
        list(pool.map(file_du_jeu, par_jeu.values()))
    for cible, morceaux in cibles.items():
        with cible.open("wb") as sortie:
            for morceau in morceaux:
                sortie.write(morceau.read_bytes())
        for morceau in morceaux:
            morceau.unlink()
        print(f"assemblé : {cible.name} ({cible.stat().st_size / 1e6:.0f} Mo)")
