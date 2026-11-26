# Dispersion of NOx from the O-I glass plant in Reims (2024) with AERMOD

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24559575.svg)](https://doi.org/10.5281/zenodo.24559575)

*[Version française : README.md](README.md)*

Independent study of atmospheric dispersion, based on public data and documented assumptions. It is **not a
regulatory assessment**: the results are indicative and have been neither checked nor validated by the operator or by
the authorities.

**Question.** What share of the NO₂ measured at the Reims monitoring stations comes from the O-I France glass plant,
the largest NOx emitter in the urban area (143 t in 2024, IREP register)? Can the monitoring network detect it?

**Report**: [`rapport/aermod_reims_report_en.pdf`](rapport/aermod_reims_report_en.pdf) (9-page summary in English;
French original: `rapport/rapport_aermod_reims.pdf`). Figures exist in both languages (`figures/*_en.png`, produced
by the same scripts with the `--en` option); detailed step reports (`rapport/*.md`) and script comments are in French.

## Main results

| Plant contribution (2024) | Rural option (reference) | Urban option (upper bound) |
|---|---|---|
| Annual mean at the 3 stations (NO₂) | 0.03 to 0.05 µg/m³ | 0.05 to 0.13 µg/m³ |
| Share of measured NO₂ at the stations | < 0.5 % | 0.5 to 1.4 % |
| Maximum annual mean (NOx), 0.7 km north-east | 0.22 µg/m³ | 0.28 µg/m³ |
| Maximum hourly value (NOx) | 49 µg/m³ (high ground, Mont de Berru) | 14 µg/m³ |

- The choice between AERMOD's rural and urban options is the main source of uncertainty (× 2 to × 4 at the stations).
  No other factor tested changes the order of magnitude: meteorology simulated at 1 km (WRF, January and July),
  roughness up to 2 m, solar radiation, fog, fumigation (AERSCREEN), stack parameters.
- The stations, 2.5–5.5 km away, cannot see the plant: its signal is 10 to 100 times smaller than the measured
  variability. Thirteen years of measurements (2013–2025), during which emissions varied by a factor of 4, disfavour
  the urban option without ruling it out.
- Hazard quotient of the plant's NO₂ contribution at sensitive establishments: ≤ 0.02 for the annual mean (WHO,
  10 µg/m³) and ≤ 0.06 for 1 h (200 µg/m³).

## Contents

| Folder | Contents |
|---|---|
| `rapport/` | reports (PDF in English and French), synthesis and step reports (French) |
| `scripts/` | Python and shell scripts: data preparation, model runs, analyses, figures |
| `figures/` | maps and figures |
| `aermet/` | AERMET inputs (stages 1 and 2), QA files (`.oqa`) and 2024 Reims-Prunay meteorology (`.sfc`, `.pfl`) |
| `aermap/` | AERMAP inputs and outputs (receptor and source elevations) |
| `aermod/` | one folder per run: inputs (`.inp`, `.rou`, building downwash) and outputs of the reference and mapped cases |
| `wrf/` | WRF `namelist.wps` and `namelist.input`; MMIF inputs and outputs for January and July 2024 (ready for AERMET) |
| `aerscreen/` | AERSCREEN runs (screening, fumigation) |
| `observations/` | hourly validated NO, NO₂, NOx and O₃ in 2024 at the three stations (LCSQA / ATMO Grand Est) |
| `donnees/` | light derived data (buildings, sensitive establishments, land use, NO₂ 2013–2025, fog) and data sources |
| `base/` | PostgreSQL / PostGIS database: schema, data and SQL queries |
| `outils/` | adapted ERA5 → WPS converter (NCAR, Apache 2.0) and Linux patch for AERSCREEN |

Large raw data are not included (WRF output ≈ 36 GB, ERA5, IREP archives, raw Météo-France and NOAA data, Landsat
and ASTER images, regulatory documents). The scripts download them; sources are listed in
`donnees/meteo_brute/SOURCES.txt`.

## Reproducing the calculations

Software (EPA, [SCRAM](https://www.epa.gov/scram)): AERMOD 26135, AERMET, AERMAP 24142, BPIPPRM, AERSCREEN 21112 and
MAKEMET; MMIF 4.1.1; WRF/WPS 4.7.1 to redo the simulated meteorology. The scripts look for executables in
`~/AERMOD/bin/` (adapt the path at the top of the scripts). AERSCREEN, distributed for Windows, compiles on Linux with
`outils/aerscreen_linux.patch` (gfortran; see `outils/LISEZMOI.txt`). In `wrf/wps*/namelist.wps`, replace
`CHEMIN/VERS/WPS_GEOG` with the WPS geographical data folder.

Python 3.12 with numpy, pandas, matplotlib, rasterio, shapely, requests (and netCDF4 for ERA5). The order of the steps
is given in [README.md](README.md) (section « Reproduire les calculs »); each script is documented in its header.

## Licences

- Code (`scripts/`, AERSCREEN patch): MIT licence (`LICENSE`).
- `outils/era5_to_int_zone.py`: modified copy of [era5_to_int](https://github.com/NCAR/era5_to_int) (NCAR), Apache 2.0
  (`outils/LICENSE-Apache-2.0.txt`).
- Texts, reports and figures: Creative Commons Attribution 4.0 (CC BY 4.0).
- Data: each provider's terms. NOAA (ISD, IGRA2): public domain. Météo-France, IGN (BD TOPO, RGE ALTI, Plan IGN),
  Géorisques (IREP) and LCSQA: Licence Ouverte Etalab 2.0. EEA (NO₂ 2013–2025): CC BY 4.0. Corine Land Cover 2018:
  © European Union, Copernicus Land Monitoring Service, EEA. The MMIF files derive from ERA5: they contain modified
  Copernicus Climate Change Service information (2026).

## Citation

Ali Ousmane Mahamat (2026). *Dispersion des NOx de la verrerie O-I de Reims (2024) avec AERMOD* (version 1.0.0).
Zenodo. https://doi.org/10.5281/zenodo.24559575 — see also `CITATION.cff`.

Author: Ali Ousmane Mahamat — ORCID [0009-0009-6013-2834](https://orcid.org/0009-0009-6013-2834)
