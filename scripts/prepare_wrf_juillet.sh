#!/bin/bash
# Prépare WRF pour juillet 2024 (28/06 00 h -> 01/08 00 h) : ERA5 NCAR -> format intermédiaire WPS -> metgrid -> real.exe.
# Même chaîne que janvier (voir donnees/meteo_brute/SOURCES.txt). À lancer une fois tous les fichiers ERA5 de juillet présents.
set -euo pipefail
# Chemins (modifiables par variables d'environnement) : dossier wrf/ du projet, outils ERA5, Python, WPS
W=${W:-$(cd "$(dirname "$0")/../wrf" && pwd)}
OUTILS=${OUTILS:-$(cd "$(dirname "$0")/../outils" && pwd)}
PY=${PY:-python3}
WPS=${WPS:-~/WRF/WPS}

# 1. Contrôle : 35 jours de fichiers (28/06 au 01/08) x 5 variables de niveaux de pression
n=$(ls $W/era5_ncar/e5.oper.an.pl.*.202406{28,29,30}00_* $W/era5_ncar/e5.oper.an.pl.*.202407*00_* $W/era5_ncar/e5.oper.an.pl.*.2024080100_* 2>/dev/null | wc -l)
echo "fichiers niveaux de pression juillet : $n / 175"
[ "$n" -eq 175 ] || { echo "incomplet, arrêt"; exit 1; }

# 2. Conversion au format intermédiaire WPS (toutes les 3 h)
cd $W/intermediaire
PYTHONPATH=$OUTILS $PY $OUTILS/era5_to_int_zone.py -i -p ../era5_ncar \
    2024-06-28_00 2024-08-01_00 3 > conversion_juillet.log 2>&1
echo "fichiers intermédiaires juillet : $(ls ERA5:2024-0[678]* | wc -l) / 273"

# 3. metgrid, avec une copie de namelist.wps aux dates de juillet
mkdir -p $W/met_em_juillet $W/wps_juillet
cd $W/wps_juillet
sed -e "s/2023-12-28_00:00:00/2024-06-28_00:00:00/g; s/2024-02-01_00:00:00/2024-08-01_00:00:00/g" \
    -e "s|../met_em_janvier/|../met_em_juillet/|" \
    -e "s|^ io_form_geogrid = 2,| io_form_geogrid = 2,\n opt_output_from_geogrid_path = '../wps/',|" $W/wps/namelist.wps > namelist.wps
sed -i "s|^ io_form_metgrid = 2,| io_form_metgrid = 2,\n opt_metgrid_tbl_path = '../wps/metgrid/',|" namelist.wps
$WPS/metgrid.exe > metgrid_juillet.out 2>&1
tail -2 metgrid_juillet.out
echo "fichiers met_em juillet : $(ls $W/met_em_juillet | wc -l) / 819"

# 4. real.exe (2 processus, pour laisser les cœurs à la simulation de janvier)
cd $W/run_juillet
ln -sf ../met_em_juillet/met_em.d0* .
mpirun -np 2 ./real.exe > real.out 2>&1
tail -1 rsl.error.0000
mkdir -p journal_real && mv rsl.* journal_real/
ls -la wrfinput_d0* wrfbdy_d01
