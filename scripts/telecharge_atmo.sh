#!/bin/bash
# Télécharge les moyennes horaires LCSQA (fichiers E2 quotidiens, data.gouv.fr) de 2024
# et ne garde que les 3 stations ATMO Grand Est de Reims (FR14010, FR14011, FR14012).
set -u
BASE=https://files.data.gouv.fr/ineris/lcsqa/concentrations-de-polluants-atmospheriques-reglementes/temps-reel/2024
SORTIE=$(dirname "$0")/../observations/brut
mkdir -p "$SORTIE"
jour() {
    local f="$SORTIE/reims_$1.csv"
    [ -s "$f" ] && return
    curl -sL --retry 3 --max-time 120 "$BASE/FR_E2_$1.csv" | grep -E "^Date|;FR1401[012];" > "$f.tmp" && mv "$f.tmp" "$f"
}
export -f jour; export BASE SORTIE
for i in $(seq 0 365); do date -d "2024-01-01 +$i day" +%F; done | xargs -P 6 -I{} bash -c 'jour {}'
echo "fichiers : $(ls "$SORTIE"/reims_*.csv | wc -l)"
