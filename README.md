# Dispersion des NOx de la verrerie O-I de Reims (2024) avec AERMOD

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24559575.svg)](https://doi.org/10.5281/zenodo.24559575)

Étude indépendante de la dispersion atmosphérique, fondée sur des données publiques et des hypothèses documentées.
Ce n'est **pas une expertise réglementaire** : les résultats sont indicatifs et n'ont été ni vérifiés ni validés par
l'exploitant ou par l'administration.

**Question.** Quelle part du NO₂ mesuré aux stations de Reims provient de la verrerie O-I France, plus gros émetteur
de NOx de l'agglomération (143 t en 2024, IREP) ? Le réseau de mesure permet-il de la mettre en évidence ?

**Rapport** : [`rapport/rapport_aermod_reims.pdf`](rapport/rapport_aermod_reims.pdf) (synthèse d'une dizaine de pages) ;
détail par étape dans `rapport/*.md`.

## Résultats principaux

| Contribution de l'usine (2024) | Option rurale (référence) | Option urbaine (borne haute) |
|---|---|---|
| Moyenne annuelle aux 3 stations (NO₂) | 0,03 à 0,05 µg/m³ | 0,05 à 0,13 µg/m³ |
| Part du NO₂ mesuré aux stations | < 0,5 % | 0,5 à 1,4 % |
| Moyenne annuelle maximale (NOx), à 0,7 km au nord-est | 0,22 µg/m³ | 0,28 µg/m³ |
| Maximum horaire (NOx) | 49 µg/m³ (relief, Mont de Berru) | 14 µg/m³ |

- Le choix de l'option rurale ou urbaine d'AERMOD est le premier facteur d'incertitude (× 2 à × 4 aux stations).
  Aucun autre facteur testé ne change l'ordre de grandeur : météo simulée à 1 km (WRF, janvier et juillet),
  rugosité jusqu'à 2 m, luminosité, brouillard, fumigation (AERSCREEN), paramètres de la cheminée.
- Les stations, à 2,5–5,6 km, ne peuvent pas voir l'usine : le signal est 10 à 100 fois plus petit que la variabilité
  mesurée. Treize ans de mesures (2013–2025), pendant lesquels les émissions ont varié d'un facteur 4, défavorisent
  l'option urbaine sans la réfuter.
- Quotient de danger de la contribution de l'usine (NO₂) : ≤ 0,02 en moyenne annuelle (OMS, 10 µg/m³) et ≤ 0,06 sur
  1 h (200 µg/m³) aux établissements sensibles.

## Contenu

| Dossier | Contenu |
|---|---|
| `rapport/` | rapport PDF, synthèse (`synthese_projet.md`) et rapports par étape |
| `scripts/` | scripts Python et shell : préparation des données, lancements, analyses, figures |
| `figures/` | cartes et figures |
| `aermet/` | entrées AERMET (étapes 1 et 2), fichiers de contrôle (`.oqa`) et météo 2024 de Reims-Prunay (`.sfc`, `.pfl`) |
| `aermap/` | entrées et sorties AERMAP (relief des récepteurs et de la source) |
| `aermod/` | un dossier par calcul : entrées (`.inp`, `.rou`, sillage des bâtiments) ; sorties des cas de référence et des cas cartographiés |
| `wrf/` | `namelist.wps` et `namelist.input` de WRF ; entrées et sorties MMIF de janvier et juillet 2024 (prêtes pour AERMET) |
| `aerscreen/` | calculs AERSCREEN (dépistage, fumigation) |
| `observations/` | NO, NO₂, NOx et O₃ horaires validés 2024 des trois stations (LCSQA / ATMO Grand Est) |
| `donnees/` | données dérivées légères (bâtiments, établissements sensibles, occupation du sol, NO₂ 2013–2025, brouillard) et liste des sources |
| `base/` | base PostgreSQL / PostGIS : schéma, données et requêtes SQL |
| `outils/` | convertisseur ERA5 → WPS adapté (NCAR, Apache 2.0) et correctif Linux d'AERSCREEN |

Les données brutes volumineuses ne sont pas incluses : sorties WRF (≈ 36 Go), ERA5, archives IREP, données Météo-France
et NOAA brutes, images Landsat et ASTER, documents réglementaires. Les scripts les téléchargent ; leurs sources sont
listées dans `donnees/meteo_brute/SOURCES.txt`.

## Reproduire les calculs

Logiciels (EPA, [SCRAM](https://www.epa.gov/scram)) : AERMOD 26135, AERMET, AERMAP 24142, BPIPPRM, AERSCREEN 21112 et
MAKEMET ; MMIF 4.1.1 ; WRF/WPS 4.7.1 pour refaire la météo simulée. Les scripts cherchent les exécutables dans
`~/AERMOD/bin/` (variable `AERMOD` ou chemin à adapter en tête des scripts). AERSCREEN, distribué pour Windows, se
compile sous Linux avec `outils/aerscreen_linux.patch` (gfortran ; voir l'en-tête du correctif).

Dans `wrf/wps*/namelist.wps`, remplacer `CHEMIN/VERS/WPS_GEOG` par le dossier des données géographiques de WPS.

Python 3.12 avec numpy, pandas, matplotlib, rasterio, shapely, requests (et netCDF4 pour ERA5).

Ordre des étapes, chaque script étant documenté en tête de fichier :
1. Météo : `controle_isd.py`, `corrige_cavok.py`, `complete_trous_mf.py`, puis AERMET (`aermet/aermet1.inp`,
   `aermet/aermet2.inp`) ; les fichiers `.oqa` fournis permettent de repartir directement de l'étape 2.
2. Relief et bâtiments : `prepare_mnt.py`, AERMAP (`aermap/aermap.inp`), `prepare_bpip.py` et BPIPPRM.
3. AERMOD : `aermod/reference_bati` (rural) et `aermod/reference_urbaine` (urbain) ; `sensibilite.py`,
   `rural_urbain.py`.
4. Mesures et comparaison : `telecharge_atmo.sh`, `observations_atmo.py`, `compare_secteurs.py`,
   `experience_naturelle.py`, `correlation_mesures.py`.
5. Météo WRF : `telecharge_era5_ncar.py`, WPS/WRF (`wrf/`), MMIF, puis `aermod_wrf_janvier.py`,
   `aermod_wrf_janvier_sensibilite.py`, `aermod_wrf_juillet.py` ; les fichiers MMIF fournis (`wrf/mmif/`) évitent de
   relancer WRF.
6. Compléments : `z0_cheminee.py`, `landsat_usine.py`, `aster_nuit_usine.py` (compte NASA Earthdata nécessaire),
   `tubes_faisabilite.py`, `nebulosite_brouillard.py`, AERSCREEN (`aerscreen/`).
7. Figures et volet sanitaire : `carte_aermod.py`, `carte_mois.py`, `points_sensibles.py`, `sensibles_fourchette.py`.

## Licences

- Code (`scripts/`, correctif AERSCREEN) : licence MIT (`LICENSE`).
- `outils/era5_to_int_zone.py` : copie modifiée d'[era5_to_int](https://github.com/NCAR/era5_to_int) (NCAR),
  licence Apache 2.0 (`outils/LICENSE-Apache-2.0.txt`).
- Textes, rapport et figures : licence Creative Commons Attribution 4.0 (CC BY 4.0).
- Données : conditions de chaque producteur. NOAA (ISD, IGRA2) : domaine public. Météo-France, IGN (BD TOPO,
  RGE ALTI, Plan IGN), Géorisques (IREP) et LCSQA : Licence Ouverte Etalab 2.0. AEE (NO₂ 2013–2025) : CC BY 4.0.
  Corine Land Cover 2018 : © Union européenne, Copernicus Land Monitoring Service, AEE. Les fichiers MMIF dérivent
  d'ERA5 : contiennent des informations modifiées du Copernicus Climate Change Service (2026).

## Citer

Mahamat Ali Ousmane (2026). *Dispersion des NOx de la verrerie O-I de Reims (2024) avec AERMOD* (version 1.0.0).
Zenodo. https://doi.org/10.5281/zenodo.24559575 — voir aussi `CITATION.cff`.

Auteur : Mahamat Ali Ousmane — ORCID [0009-0009-6013-2834](https://orcid.org/0009-0009-6013-2834)
