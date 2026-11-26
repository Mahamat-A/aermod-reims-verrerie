# Dispersion des NOx de la verrerie O-I de Reims en 2024 — modélisation AERMOD et comparaison aux mesures

Synthèse du projet personnel, état au 26/11/2026 (étapes 0 à 8 et 10 ; étape 8 : WRF → MMIF → AERMOD, janvier et juillet 2024).
Auteur : Mahamat Ali Ousmane. Détails : rapports par étape (§ 8) et `PLAN.md`.

## 1. Question
Quelle part du NO₂ mesuré à Reims provient de la verrerie O-I France, plus gros émetteur de NOx de
l'agglomération (143 t en 2024, IREP), et le réseau de mesure permet-il de la mettre en évidence ?

## 2. Données et méthode
| Élément | Source | Traitement |
|---|---|---|
| Source | Arrêté préfectoral 2025-APC-277-IC, IREP, rapports d'inspection (Géorisques) | Cheminée unique 59 m, 523 K, 8 m/s, Ø 2,51 m ; position par triangulation Street View + orthophoto IGN ; débits 2024 répartis selon la production (arrêt du four 3 le 12/07), `EMISFACT` mensuel |
| Météo | NOAA ISD Reims-Prunay, Météo-France (base horaire), radiosondages IGRA Trappes / Idar-Oberstein | AERMET 26135, surface autour du mât de Prunay (z0 0,03–0,15 m selon la saison, convention de l'EPA pour un vent mesuré) ; nébulosité CAVOK/NSC/NCD → 0 octa (validé par l'ensoleillement mesuré : 52,5 min/h) ; 381 heures complétées par Météo-France ; 60 sondages de secours ; 98–100 % d'heures utilisables par trimestre |
| Relief | IGN RGE ALTI 25 m | AERMAP, grille 20 × 20 km au pas de 250 m (6 561 points) + 3 stations |
| Bâtiments | IGN BD TOPO (599 bâtiments ≥ 3 m) | BPIPPRM : silo de 31,9 m à 30 m, hauteur BPE 77,2 m |
| Milieu | Corine Land Cover 2018, BD TOPO (logements) | Fourchette rurale–urbaine : Auer → rural (24 % de sols urbains), densité ≈ 3 000 hab/km² → urbain (seuil EPA 750) |
| Mesures | LCSQA / ATMO Grand Est (valeurs validées 2024) | Jean d'Aulan, Doumer, Bétheny : NO, NO₂, NOx, O₃ ; couverture 91–97 % |
| Chimie | Ozone mesuré | NO₂ = 0,9 × NOx (OLM = ARM2 : ozone toujours en excès) |

Les données sont aussi rangées dans une base PostgreSQL / PostGIS (`base/`), où les analyses sont
reproduites en SQL.

## 3. Résultats : fourchette rurale–urbaine (bâtiments inclus)
Les deux critères de l'EPA se contredisent : la méthode d'Auer (occupation des sols) donne rural,
la densité de population donne urbain. Les mesures de 2013 à 2025 défavorisent l'option urbaine
aux stations, sans la réfuter (§ 4). Les résultats sont donc donnés en fourchette **rural – urbain** :

| Indicateur (contribution de l'usine, 2024) | Rural | Urbain |
|---|---|---|
| Moyenne annuelle maximale (NOx), à 0,7 km au nord-est | 0,22 µg/m³ | 0,28 µg/m³ |
| Maximum horaire (NOx) | **49 µg/m³** (Mont de Berru) | 14 µg/m³ |
| Moyenne annuelle aux 3 stations (NO₂) | 0,03 à 0,05 µg/m³ | 0,05 à 0,13 µg/m³ |
| Part du NO₂ mesuré aux stations | < 0,5 % | 0,5 à 1,4 % |

- Aucune des deux options n'est la plus prudente partout : l'urbaine donne davantage en moyenne
  annuelle, la rurale en maximum horaire (relief).
- **Comparaison 2024** : les variations du NO₂ mesuré avec le vent (facteur 2 à 3) sont dues aux
  situations météorologiques (vents de NE froids et stables) et au trafic, pas à l'usine. Le signal
  attendu est sous le seuil de détection des moyennes mesurées (± 2 à 10 µg/m³).
- Cartes : `figures/aermod_rural_2024_*.png` et `figures/aermod_reference_2024_*.png` (urbain) ; cartes
  mensuelles de janvier et juillet (Prunay et WRF) : `figures/etape8_{janvier,juillet}_*.png`.
  Les deux moyennes annuelles partagent leurs classes ; chaque carte horaire a les siennes (première
  classe ≈ le quart du maximum) : on ne compare pas leurs couleurs, mais leurs valeurs.

## 4. Incertitudes (un paramètre à la fois)
| Hypothèse | Effet sur les concentrations |
|---|---|
| Rural ou urbain | le facteur dominant : stations ×2 à ×4,6, maximum horaire −72 % |
| Météo à 7 km, en campagne (WRF à 1 km, janvier et juillet) | stations : × 1,2 à × 5,7 en hiver avec la surface de la maille WRF (z0 0,8 m, règle de l'EPA), × 1,2 à × 2,7 avec z0 0,25 m estimé autour de la source ; × 0,6 à × 1 en été ; toujours ≤ 0,17 µg/m³ en option rurale, ≤ 0,26 en urbaine |
| Rugosité z0 0,03 → 0,25 m (vent de Prunay, test hors convention) | + 18 à 20 % aux stations (moyenne annuelle) |
| Rugosité forte, z0 1 à 2 m (vent WRF) | janvier : stations ≈ × 2 par rapport à z0 0,25 m (≤ 0,17 µg/m³) ; juillet : sans effet. Au-delà de 1,4 m, AERMET rejette le vent à 10 m (vent de référence ≥ 7 z0) |
| Température des fumées ± 50 °C | ± 10 à 20 % |
| Émissions déclarées | proportionnel (± 20 % → ± 20 %) |
| Diamètre, position A/B, bâtiments, découpage horaire de juillet | < 7 % |
| Nébulosité recalculée sur le rayonnement mesuré (Météo-France) | + 8 à 12 % au maximum annuel, 0 à + 6 % aux stations |
| Brouillard (112 h/an) et fumigation | contribution rurale quasi nulle pendant le brouillard ; fumigation du matin (AERSCREEN, absente d'AERMOD) : 6,5 µg/m³ de NOx sur 1 h à 9,3 km, sous les autres maxima horaires |

**Rugosité : quelle surface pour quel vent (corrigé les 25 et 26/11 d'après les guides de l'EPA).** Avec un vent
**mesuré**, AERMET déduit la turbulence de ce vent : il faut la surface **au site de mesure** (Prunay, champs :
z0 0,03 m en hiver, jusqu'à 0,15 m en été ; guide AERMET, § 3.7.10). Avec un vent **simulé** (WRF via MMIF), il faut
la surface **de la maille du modèle** fournie par MMIF (guide MMIF, § 3.3) : z0 0,8 m, la maille de 1 km étant classée
urbaine. Le z0 ≈ 0,25 m estimé dans 1 km autour de la cheminée (Corine) n'est qu'une variante. Le calcul « vent de
Prunay + z0 0,25 m » (`aermet/z0_025/`) est un **test de sensibilité** (+ 18 à 20 % aux stations en moyenne
annuelle), pas l'estimation de référence. Celle-ci est l'option rurale avec la surface de Prunay.

**Test par les mesures (expérience naturelle 2013–2025).** Les émissions d'O-I ont varié d'un
facteur 4 (143 à 566 t/an). Le NO₂ mesuré par vent venant de l'usine, comparé aux secteurs voisins,
ne suit pas ces variations. Le rapport pente mesurée / pente modélisée vaut −0,16 ± 0,22 pour
l'option urbaine et −0,08 ± 0,65 pour l'option rurale, si le vent de Prunay donnait exactement la
direction du panache. Or l'écart de direction entre WRF (1 km, maille de l'usine) et Prunay a un
écart type robuste de 26° en janvier 2024 et de 38° en juillet : avec une erreur de direction de 20 à 40°, l'option
urbaine n'est plus défavorisée qu'à 1,1–2,2 σ, et l'option rurale reste compatible (avec la
surface de Prunay, comme avec le test de sensibilité à z0 = 0,25 m, voir ci-dessus). Le test indique une préférence, il ne tranche pas ; heure par heure non plus
(`rapport/etape8_rural_urbain.md`). Le modèle d'ATMO (suppression de toute
l'industrie : −2 µg/m³ au plus) donne le même ordre de grandeur. Détails :
`rapport/etape6_comparaison.md`, figure `figures/etape6_experience_naturelle.png`.

## 5. Conclusions
1. La verrerie contribue pour **moins de 0,5 % (rural) à 1,4 % (urbain) du NO₂ moyen** mesuré aux
   stations de Reims ; le NO₂ urbain est dominé par le trafic et les conditions météorologiques.
2. Le réseau ne voit pas directement l'usine, mais 13 ans de mesures et une variation des émissions
   d'un facteur 4 permettent un **test** : il défavorise l'option urbaine aux stations (1,1–2,2 σ
   avec une erreur réaliste sur la direction du vent), l'option rurale est compatible. Une validation directe
   demanderait des mesures horaires sous le panache (analyseurs NOx/SO₂ et vent mesuré à 0,5–1 km au nord-est,
   tri des heures selon la direction du vent) : des tubes passifs ne suffiraient pas, l'apport de l'usine en
   moyenne sur 14 jours (0,1–0,8 µg/m³ de NO₂) étant bien inférieur à leur incertitude (`scripts/tubes_faisabilite.py`).
3. Le choix rural/urbain d'AERMOD est la principale source d'incertitude. Les critères de l'EPA
   se contredisent ici, et 13 ans de mesures défavorisent l'option urbaine sans la réfuter : les
   résultats sont donnés en fourchette, et l'évaluation sanitaire retient le pire des deux.
4. Aucun autre facteur testé ne change l'ordre de grandeur : météo simulée à 1 km (WRF, hiver et été), rugosité
   jusqu'à 2 m, luminosité, brouillard, fumigation (AERSCREEN), paramètres de cheminée. L'usine ne compte qu'à
   proximité (moins de 1 km au nord-est) et, certaines heures, sur le relief (Mont de Berru, Montagne de Reims).

## 6. Reproductibilité
Scripts Python dans `scripts/`, entrées AERMOD/AERMET/AERMAP dans `aermod/`, `aermet/`, `aermap/`,
corrections de données documentées dans `donnees/meteo_corrigee/LISEZMOI.txt`, sources dans
`donnees/meteo_brute/SOURCES.txt`, requêtes SQL dans `base/requetes/`, calculs AERSCREEN dans `aerscreen/`. Anciennes versions des
rapports : `rapport/archives/`.

## 7. Volet risques sanitaires
173 établissements sensibles à moins de 4 km (BD TOPO). Contribution de la verrerie au NO₂, rural –
urbain : au plus 0,10 – 0,19 µg/m³ en moyenne annuelle, 2,1 µg/m³ sur 24 h et 11,0 – 10,4 µg/m³ sur
1 h. En retenant le pire des deux options, le quotient de danger de la verrerie est ≤ 0,02
(valeur guide annuelle de l'OMS, 10 µg/m³) et ≤ 0,06 sur 1 h (200 µg/m³). L'exposition totale
(≈ 9,5 µg/m³) est dominée par le fond urbain. Détails : `rapport/etape10_risques_sanitaires.md`.

## 8. Rapports détaillés
| Fichier | Contenu |
|---|---|
| `rapport/etape6_comparaison.md` | comparaison 2024 aux stations par secteur de vent ; expérience naturelle 2013–2025 |
| `rapport/etape7_incertitudes.md` | sensibilité aux paramètres de source, bâtiments, option rurale/urbaine |
| `rapport/etape8_wrf.md` | météo WRF à 1 km (janvier, juillet), surface de la maille, rugosité jusqu'à 2 m, règle de surface |
| `rapport/etape8_rural_urbain.md` | expérience naturelle avec l'erreur de direction mesurée, littérature, Landsat, ASTER, confrontation horaire, faisabilité d'une validation |
| `rapport/etape8_luminosite_brouillard.md` | rayonnement vu par AERMET, brouillard, fumigation (AERSCREEN) |
| `rapport/etape10_risques_sanitaires.md` | établissements sensibles, quotients de danger |
