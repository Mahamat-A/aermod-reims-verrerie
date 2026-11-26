# Étape 8 (suite) — Luminosité, brouillard et fumigation

État au 26/11/2026. Question : AERMET voit-il bien le rayonnement et le brouillard, et AERMOD manque-t-il un phénomène
(la fumigation du matin) qui changerait les maxima horaires ? Météo et rugosité : `etape8_wrf.md`.

## Résultats (26/11) — `scripts/nebulosite_brouillard.py`
Données : Météo-France, poste Reims-Prunay 51449002, horaire 2024 : rayonnement global (GLO), durée d'insolation (INS),
visibilité (VV), temps présent (WW). Résultats intermédiaires dans `donnees/brouillard/`.

**Luminosité.** AERMET ne mesure pas le rayonnement : il l'estime à partir de la nébulosité (Kasten-Czeplak).
Sur 3 518 heures de jour (soleil > 10°) : 263 W/m² estimés contre 290 mesurés (−9 %), r = 0,86, écart > 100 W/m² une
heure sur quatre. Par ciel couvert (9–10/10, 2 173 h), AERMET sous-estime le rayonnement de 32 % (140 contre 206 W/m²) ;
par ciel clair, il le surestime de 11 %.
Variante : le jour, nébulosité recalculée pour redonner le rayonnement mesuré (`aermet/rayonnement/`, `aermod/rayonnement_*`) ;
moins d'heures extrêmes (clair 38 → 14 %, couvert 44 → 26 % des heures modifiées), flux de chaleur médian de jour 22 → 29 W/m²,
couche convective médiane 427 → 490 m.

| Cas (année 2024, NOx µg/m³) | max annuel | max 1 h | Jean d'Aulan / Doumer / Bétheny |
|---|---|---|---|
| rural, nébulosité observée (référence) | 0,218 | 49,2 | 0,031 / 0,055 / 0,030 |
| rural, nébulosité du rayonnement mesuré | 0,244 (+12 %) | 49,2 | 0,033 / 0,057 / 0,030 |
| urbain, nébulosité observée | 0,283 | 13,6 | 0,140 / 0,127 / 0,059 |
| urbain, nébulosité du rayonnement mesuré | 0,305 (+8 %) | 13,1 | 0,141 / 0,127 / 0,058 |

→ Effet faible (stations 0 à +6 %) : la luminosité n'est pas une source d'incertitude importante ici.

**Brouillard.** 112 heures à visibilité < 1 km en 2024 (1,3 % de l'année ; 41 épisodes ; surtout d'octobre à janvier, la
nuit et le matin ; WW 44–49 : brouillard, givrant ou non). Pendant ces heures, AERMET décrit une couche limite stable
(78 % des heures, contre 58 % le reste du temps), vent 1,5 m/s, u* 0,09 m/s, couche de mélange 67 m.
- **Anomalie** : 14 % des heures de brouillard sont vues par AERMET comme un ciel clair (nébulosité 0, ciel « obscurci »
  mal codé). AERMET les refroidit alors comme une nuit claire, alors qu'une couche de brouillard est presque neutre en
  son sein et freine le refroidissement du sol. Effet limité (≈ 16 h dans l'année).
- **NOx mesuré ×2 à ×3,5** pendant le brouillard (Jean d'Aulan 35,6 contre 12,4 ; Doumer 92,4 contre 47,6 ; Bétheny 43,1
  contre 12,4 µg/m³) : air stagnant, le trafic s'accumule.
- **Contribution modélisée de l'usine quasi nulle en rural** (0,001–0,025 µg/m³) : le panache chaud (hauteur effective
  ≈ 125–135 m) reste au-dessus d'une couche de mélange de 67 m. En urbain, elle triple à Jean d'Aulan (0,39) : l'option
  urbaine impose une turbulence nocturne qui rabat le panache.
- **Après la levée du brouillard le matin** (46 h, 3 h suivant 41 levées) : AERMOD rural rabat une partie du panache
  quand la couche convective se forme (Doumer 0,33 µg/m³ en moyenne, maximum horaire 5,7, contre 0,05 d'ordinaire).

**Fumigation** (le panache resté en altitude la nuit est rabattu d'un coup quand l'inversion se dissipe le matin).
AERMOD ne la simule pas ; l'EPA la traite dans **AERSCREEN** (équations de SCREEN3, Turner 1970), installé le 26/11
(`~/AERMOD/bin/aerscreen`, portage Linux validé sur le cas test EPA « point, terrain plat, sillage » : résultats
identiques à la référence, fumigation comprise). Entrée : `aerscreen/rural_z025/` (cheminée 59 m, 523 K, 8 m/s,
Ø 2,51 m, 4,53 g/s de NOx ; météo de dépistage MAKEMET, z0 0,25 m, albédo 0,19, Bowen 0,45 ; 262–309 K).

| AERSCREEN (NOx, µg/m³, 1 h) | z0 0,25 m (source) | z0 0,03 m (Prunay) |
|---|---|---|
| Maximum, terrain plat, toutes météos | 12,3 à 2,0 km | 16,7 à 1,9 km |
| Limite de propriété (100 m) | 10,0 | 4,2 |
| **Fumigation (levée d'inversion)** | **6,5 à 9,3 km** | aucune heure ne remplit les critères |

- AERSCREEN place la fumigation là où la couche mélangée du matin atteint le sommet du panache : panache à 159 m,
  vent de 2,5 m/s au sommet de la cheminée, classe F ; il faut environ une heure de chauffage solaire, soit **9,3 km**.
  À cette distance, le panache s'est élargi (σy ≈ 460 m) : **6,5 µg/m³** de NOx, moins que les autres maxima horaires.
- **Correction** : ma première estimation à la main (Turner, 20–100 µg/m³ à 1–5 km) supposait la fumigation près de
  l'usine avec un panache encore étroit. C'était faux : AERSCREEN montre qu'il faut près d'une heure de chauffage pour
  atteindre le panache, et qu'il s'est élargi entre-temps. Elle est remplacée par la valeur AERSCREEN.
- Sans relief ni bâtiments, AERSCREEN donne 12–17 µg/m³ sur 1 h, du même ordre que les maxima horaires d'AERMOD en
  terrain plat (urbain 13,6) ; le maximum d'AERMOD rural (49 µg/m³) vient du relief, qu'AERSCREEN n'a pas ici.
- Conséquence sanitaire : fumigation ≈ 5,9 µg/m³ de NO₂ à 9 km, soit un quotient de danger horaire de 0,03 ;
  le 0,06 de l'étape 10 reste la valeur la plus élevée.
