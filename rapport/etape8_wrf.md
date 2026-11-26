# Étape 8 — Météo WRF à 1 km (janvier et juillet 2024) et rugosité du site

État au 26/11/2026. Question : la météo de Reims-Prunay (à 7 km à l'est-sud-est, en campagne) biaise-t-elle le résultat ? On refait
AERMOD avec la météo simulée par WRF à la maille de l'usine. WRF 4.7.1, domaines 9/3/1 km, forçage ERA5 (NCAR) ;
janvier : 28/12/2023 → 01/02/2024 ; juillet : 28/06 → 01/08/2024 (« SUCCESS COMPLETE WRF » les deux fois).
Chaîne : `wrf/mmif/{janvier,juillet}/` (MMIF 4.1.1, mode AERMET, maille de la cheminée, 744 h) → AERMET PROG (LOCATION
ajoutée dans METPREP, sinon E71) → `scripts/aermod_wrf_janvier.py`, `aermod_wrf_janvier_sensibilite.py`,
`aermod_wrf_juillet.py` (aermod/{jan,jul}_<météo>_<option>/ : même source, mêmes bâtiments et récepteurs, STARTEND
du mois, moyenne PERIOD). Tableaux : `scripts/resultats_wrf_mois.py jan|jul` ; cartes : `scripts/carte_mois.py jan|jul`
(figures/etape8_{janvier,juillet}_{moyenne,max1h}.png).
Suite de l'étape : `etape8_rural_urbain.md` (mesures, satellites, littérature) et `etape8_luminosite_brouillard.md`.

## Météo de surface (janvier, 744 h)
| | WRF (maille de l'usine) | Prunay |
|---|---|---|
| z0 | 0,80 m (maille bâtie) | 0,03 m |
| Bowen | 5,67 (douteux en janvier) | 0,45 |
| u* médian | 0,69 m/s | 0,23 m/s |
| L médian la nuit | 1 561 m (quasi neutre) | 60 m (stable) |
| zim nuit / zic jour (médianes) | 425 / 372 m | 227 / 154 m |
| vent moyen | 4,6 m/s | 4,0 m/s (r = 0,84) |
| écart de direction WRF − Prunay | médiane |Δ| 16–19°, écart-type 38–47°, biais +11° | |

## Contribution de l'usine (NOx, µg/m³, janvier)
| Cas | max moyenne janvier (lieu) | max 1 h (lieu) | Jean d'Aulan / Doumer / Bétheny |
|---|---|---|---|
| Prunay, rural | 0,25 (6,5 km, 47°) | 41,5 (8,5 km, 178°) | 0,025 / 0,029 / 0,044 |
| WRF, rural | 1,78 (0,4 km, 45°) | 18,5 (8,2 km, 192°) | 0,115 / 0,164 / 0,054 |
| Prunay, urbain | 0,41 (1,4 km, 45°) | 12,6 (1,0 km, 194°) | 0,195 / 0,115 / 0,078 |
| WRF, urbain | 1,92 (0,4 km, 45°) | 16,4 (0,6 km, 117°) | 0,222 / 0,237 / 0,077 |

## Lecture (janvier)
- Avec WRF, la couche limite à l'usine est presque neutre et très turbulente (z0 = 0,8 m, u* triplé) : le panache
  est rabattu près de la source (maximum mensuel à 0,4 km, 7 fois la valeur Prunay-rural) et l'option rurale avec
  WRF donne aux stations des valeurs proches de l'option urbaine avec Prunay.
- L'écart rural/urbain se réduit fortement avec WRF : la météo WRF « contient » déjà une partie de l'effet urbain.
- Un seul mois d'hiver ne suffisait pas : la surface de la maille WRF (z0, Bowen) et juillet sont traités plus bas.
- L'écart de direction WRF–Prunay (σ ≈ 40°, médiane 16–19°) est du même ordre que les valeurs testées dans
  l'expérience naturelle (σ = 10–30°) ; ce n'est pas l'erreur vraie de Prunay mais une borne de représentativité.

## Sensibilité (24/11) — `scripts/aermod_wrf_janvier_sensibilite.py`
Vent, température et nuages de WRF conservés ; on change la surface ou le mode MMIF.

| Cas (rural / urbain) | u* médian | L nuit médian | max janvier (µg/m³) | stations JdA / Doumer / Bétheny (rural) |
|---|---|---|---|---|
| WRF (z0 0,80, Bowen 5,67) | 0,69 | 1 561 m | 1,78 / 1,92 | 0,115 / 0,164 / 0,054 |
| WRF, Bowen 0,45 (z0 0,80) | 0,69 | 1 593 m | 1,69 / 1,82 | 0,111 / 0,166 / 0,053 |
| WRF, surface de Prunay (z0 0,03, Bowen 0,45) | 0,24 | 162 m | 0,41 / 0,54 | 0,036 / 0,058 / 0,035 |
| WRF, mode MMIF direct (PBL de WRF) | 0,38 | 369 m | 0,71 / 0,96 | 0,081 / 0,139 / 0,074 |
| Prunay (rappel) | 0,23 | 60 m | 0,25 / 0,41 | 0,025 / 0,029 / 0,044 |

- Le Bowen n'a presque aucun effet ; **la rugosité z0 de la maille WRF (0,8 m) explique l'essentiel** de l'écart
  avec Prunay. Avec la surface de Prunay, la météo WRF donne des valeurs proches de Prunay (× 1,4 à 2 aux stations).
- Le vent et la température de WRF ne sont donc pas la cause principale ; la question redevient celle du z0
  représentatif autour de la cheminée (même question que rural/urbain), traitée au paragraphe suivant.
- Mode direct : intermédiaire, mais un maximum horaire de 169 µg/m³ en rural (heure isolée à couche de mélange WRF
  très basse) à examiner avant toute utilisation.

## Balayage de z0 (météo WRF, Bowen 0,45, albédo 0,19) et z0 estimé autour de la cheminée
| z0 (m) | u* médian | L nuit médian | rural : max janv. / JdA, Doumer, Bétheny | urbain : max janv. / JdA, Doumer, Bétheny |
|---|---|---|---|---|
| 0,03 | 0,24 | 162 m | 0,41 / 0,036, 0,058, 0,035 | 0,54 / 0,145, 0,249, 0,085 |
| 0,1 | 0,31 | 262 m | 0,60 / 0,042, 0,060, 0,044 | 0,72 / 0,163, 0,254, 0,087 |
| 0,2 | 0,38 | 376 m | 0,77 / 0,053, 0,070, 0,052 | 0,91 / 0,177, 0,255, 0,086 |
| 0,25 | 0,40 | 446 m | 0,87 / 0,058, 0,078, 0,055 | 0,99 / 0,183, 0,255, 0,085 |
| 0,3 | 0,43 | 506 m | 0,96 / 0,063, 0,088, 0,057 | 1,07 / 0,188, 0,254, 0,085 |
| 0,5 | 0,53 | 780 m | 1,20 / 0,085, 0,134, 0,061 | 1,31 / 0,203, 0,252, 0,083 |
| 0,8 | 0,69 | 1 593 m | 1,69 / 0,111, 0,166, 0,053 | 1,82 / 0,218, 0,238, 0,075 |

`scripts/z0_cheminee.py` (méthode AERSURFACE : rayon 1 km, moyenne géométrique pondérée par 1/distance, valeurs
d'hiver approximatives par classe Corine) : **z0 ≈ 0,25 m** (secteurs 0,14 à 0,45 m). Les valeurs par classe sont
des ordres de grandeur.

- Avec z0 ≈ 0,2–0,3 m (estimation de la surface réelle autour de la source ; ce n'est pas la règle de l'EPA, qui
  demande la surface de la maille WRF fournie par MMIF, voir l'encadré ci-dessous), l'option rurale donne aux stations environ 2 fois les valeurs Prunay-rural
  (JdA 0,05–0,06 contre 0,025) et un maximum mensuel 3 à 4 fois plus fort, situé à moins de 1 km.
- La sensibilité de l'option urbaine à z0 est faible aux stations (l'option urbaine impose déjà sa propre turbulence).
- L'expérience naturelle a été refaite avec l'écart de direction mesuré entre WRF et Prunay
  (`etape8_rural_urbain.md`) ; juillet est traité plus bas.

> **Quelle surface pour quel vent (corrigé le 25/11 puis le 26/11, d'après les guides de l'EPA).**
> Vent **mesuré** (Prunay) : AERMET déduit u* du vent mesuré à 10 m ; il faut la surface **au site de mesure**
> (guide AERMET EPA-454/B-26-005, § 3.7.10 ; AERSURFACE autour du mât : champs, z0 0,03 m en hiver). Vent **simulé**
> (WRF via MMIF) : il faut la surface **de la maille du modèle**, telle que MMIF la fournit, cohérente avec le vent
> et la turbulence de WRF (guide MMIF EPA-454/B-24-005, § 3.3, et Appendix W § 8.4.2(b)) : ici z0 0,80 m (maille
> classée « urbaine »). La valeur z0 ≈ 0,25 m estimée autour de la cheminée n'est donc pas la règle de l'EPA :
> c'est une estimation de la surface réelle, utilisée comme **variante**, la maille WRF de 1 km étant entièrement
> classée urbaine alors que le kilomètre autour de la cheminée est à moitié ouvert ou boisé (Corine). Le calcul
> « vent de Prunay + z0 0,25 m » (`aermet/z0_025/`, utilisé dans `etape8_rural_urbain.md`) est un **test de
> sensibilité** (+ 18 à 20 % aux stations en moyenne annuelle 2024), pas l'estimation de référence.
> Référence : rural, surface de Prunay. Météo WRF selon la règle de l'EPA : surface MMIF (cas `wrf_*`).

## Rugosité forte : z0 = 1 / 1,5 / 2 m (26/11)
Vent WRF, albédo 0,19, Bowen de Prunay (0,45 en janvier, 0,35 en juillet) ; `aermod/{jan,jul}_wrf-z0_{1,1.5,2}_*`.

| z0 (vent WRF) | janvier : max du mois / stations rural | juillet : max du mois / stations rural | hauteur du vent de référence (AERMET) |
|---|---|---|---|
| 0,25 m | 0,87 / 0,058, 0,078, 0,055 | 0,59 / 0,054, 0,048, 0,018 | 10 m |
| 0,8 m (Bowen 0,45) | 1,69 / 0,111, 0,166, 0,053 | — | 10 m |
| 1 m | 2,14 / 0,112, 0,144, 0,046 | 0,93 / 0,057, 0,046, 0,018 | 10 m |
| 1,5 m | 1,65 / 0,116, 0,171, 0,051 | 0,88 / 0,053, 0,044, 0,018 | **30 m** |
| 2 m | 2,02 / 0,121, 0,158, 0,046 | 0,96 / 0,054, 0,044, 0,017 | **30 m** |

- **Anomalie : la réponse n'est pas monotone** (janvier : 2,14 à z0 1 m, 1,65 à 1,5 m, 2,02 à 2 m). Cause : AERMET n'accepte
  comme vent de référence qu'un niveau situé à au moins **7 × z0** au-dessus du sol. Au-delà de z0 ≈ 1,43 m, le vent
  à 10 m est rejeté et AERMET prend le niveau suivant de MMIF (30 m, vent moyen 6,1 au lieu de 4,6 m/s en janvier) :
  u* retombe de 0,84 à 0,70 m/s. C'est un **artefact de la chaîne**, pas un effet physique. Conséquence pratique :
  avec un vent mesuré seulement à 10 m (Prunay), AERMOD ne peut pas traiter z0 > 1,4 m ; il faut un vent mesuré
  au-dessus des toits (≥ 7 z0), ce qui rejoint la règle « surface autour du mât ».
- **Ordre de grandeur inchangé** : avec z0 = 2 m, les stations reçoivent au plus 0,12–0,16 µg/m³ en janvier (≈ 2 × z0
  0,25 m ; < 1 % du NOx mesuré, 20–66 µg/m³ en moyenne) ; en juillet, z0 n'a presque plus d'effet (convection).

## Juillet 2024 (26/11) — `scripts/aermod_wrf_juillet.py`, tableau par `scripts/resultats_wrf_mois.py jul`
WRF 4.7.1, mêmes domaines 9/3/1 km, ERA5, 28/06 → 01/08/2024 (« SUCCESS COMPLETE WRF », 40 h 30 sur 8 cœurs ; 28–29/06
écartés comme mise en route). MMIF 4.1.1 (`wrf/mmif/juillet/`, 744 h, 01/07 01 h → 31/07 24 h), AERMET PROG avec
LOCATION dans METPREP. 16 calculs AERMOD sans erreur (`aermod/jul_*`).

| Météo de surface (juillet) | WRF (maille de l'usine) | Prunay |
|---|---|---|
| z0 / Bowen | 0,80 m / 7,25 | 0,15 m / 0,35 |
| u* médian (nuit) | 0,54 (0,35) m/s | 0,24 (0,13) m/s |
| L médian la nuit | 419 m | 28 m |
| zic médian le jour | 1 034 m | 679 m |
| vent moyen | 3,4 m/s | 2,6 m/s (r = 0,65) |
| écart de direction WRF − Prunay (vent ≥ 1 m/s) | médiane |Δ| 28°, biais +8°, **σ robuste 38°** (brut 62°, 17 % > 90°) | |

| Cas (NOx, µg/m³, juillet) | max moyenne du mois (lieu) | max 1 h (lieu) | Jean d'Aulan / Doumer / Bétheny |
|---|---|---|---|
| Prunay, rural (référence) | 0,39 (0,7 km, 45°) | 21,8 (7,1 km, 72°) | 0,057 / 0,073 / 0,024 |
| Prunay, urbain | 0,44 (0,7 km, 45°) | 7,5 (0,5 km, 90°) | 0,142 / 0,130 / 0,055 |
| WRF, rural (z0 0,80 de MMIF) | 1,07 (0,4 km, 45°) | 8,5 (0,4 km, 315°) | 0,050 / 0,042 / 0,019 |
| WRF, urbain | 1,21 (0,4 km, 45°) | 13,1 (0,9 km, 56°) | 0,106 / 0,127 / 0,035 |
| WRF, z0 0,25 (source), rural | 0,59 (0,5 km, 90°) | 9,2 (10,2 km, 158°) | 0,054 / 0,048 / 0,018 |
| WRF, z0 0,25 (source), urbain | 0,65 (0,7 km, 45°) | 10,6 (1,2 km, 53°) | 0,109 / 0,144 / 0,038 |
| WRF, surface d'été de Prunay (z0 0,15), rural | 0,52 (0,5 km, 90°) | 9,2 (10,2 km, 158°) | 0,053 / 0,049 / 0,018 |
| WRF, surface d'été de Prunay, urbain | 0,59 (0,7 km, 45°) | 9,2 (1,2 km, 53°) | 0,109 / 0,147 / 0,039 |

(Juillet : four 3 arrêté le 12/07, même `EMISFACT` dans tous les cas.)

**Lecture.**
- **En été, WRF et Prunay s'accordent aux stations.** En option rurale, WRF (quelle que soit la surface) donne
  0,04–0,05 µg/m³ à Jean d'Aulan et Doumer, comme Prunay (0,06–0,07) ; Bétheny est même un peu plus bas. Le jour,
  la convection (zic 700–1 000 m, 56–58 % d'heures instables dans les deux cas) domine la dispersion et la
  rugosité compte peu. C'est l'inverse de janvier, où la turbulence mécanique liée à z0 faisait tout (WRF-rural
  ≈ 4 × Prunay-rural aux stations).
- **Le z0 de la maille WRF (0,8 m) joue encore près de la source** : maximum mensuel 1,07 µg/m³ à 0,4 km, contre
  0,59 avec z0 0,25 et 0,39 avec Prunay. Il ne change presque rien au-delà de quelques kilomètres.
- **En juillet, WRF redonne aux stations les valeurs de la référence** (Prunay, surface du mât) : × 0,6 à × 0,9 avec
  la surface MMIF (règle de l'EPA, z0 0,8 m), ± 35 % avec la variante z0 0,25 m. En janvier, WRF les majore :
  × 1,2 à × 5,7 avec la surface MMIF, × 1,2 à × 2,7 avec z0 0,25 m. Sur les deux mois, WRF ne remet donc pas en
  cause l'ordre de grandeur de la référence (stations ≤ 0,17 µg/m³ en rural, ≤ 0,26 en urbain).
- **Rural/urbain** : écart × 1,8 à × 3 aux stations en juillet, avec les deux météos ; le choix d'option reste le
  premier facteur d'incertitude, devant la météo.
- **Maximum horaire** : plus faible qu'en janvier avec WRF (8–13 µg/m³) ; avec Prunay-rural, 21,8 µg/m³ à 7 km au
  nord-est (relief), dans la fourchette annuelle déjà connue.
- **Direction du vent** : l'écart WRF − Prunay est plus large en été (σ robuste 38°, contre 26° en janvier ; vents
  plus faibles et convectifs). L'erreur de direction réaliste pour l'expérience naturelle est donc plutôt
  20–40° selon la saison, ce qui affaiblit encore le test contre l'option urbaine (1,1–2,2 σ d'après le tableau
  ci-dessus).

## Ce que dit la littérature sur WRF → MMIF → AERMOD (lu le 24/11)
**EPA (2018), MMIF Evaluation TSD, EPA-454/R-18-002** (texte intégral lu) — trois cas réels : Gibson (IN, SO₂,
cheminées 152–189 m, WRF 12 km), Martins Creek (PA, SO₂, 183 m, WRF 1 et 4 km), Herculaneum (MO, plomb,
WRF 4/12/36 km). MMIF passé par AERMET, surfaces issues de MMIF (pas d'AERSURFACE).
- Mêmes écarts que chez nous : avec MMIF, flux de chaleur, u*, w* et hauteurs de mélange sont **plus forts**, le
  gradient de température potentielle **plus faible** (couche limite moins stable) que avec les observations.
- La rugosité dépend de la maille : à Baldwin, z0 MMIF très faible car la maille WRF est « eau » (lac de
  refroidissement) ; à Evansville, z0 MMIF > 0,3 m l'hiver ; à Martins Creek, comparable au site.
- Résultats AERMOD : Gibson, données pronostiques non significativement différentes des observées ; Martins Creek,
  le mât sur site fait mieux, mais WRF ≈ station NWS représentative. Conclusion de l'EPA : les données
  pronostiques font « pas plus mal qu'une station NWS représentative », et « de petites différences de vent ou de
  température peuvent conduire à des résultats très différents ».

## Conclusion de l'étape 8 (météo)
- WRF ne change pas l'ordre de grandeur : stations ≤ 0,17 µg/m³ en rural et ≤ 0,27 en urbain dans tous les cas (mode MMIF direct compris), y compris z0 = 2 m.
- En hiver, tout dépend de la rugosité : WRF avec la surface MMIF (z0 0,8 m, règle de l'EPA) donne × 1,2 à × 5,7
  aux stations, la variante z0 0,25 m × 1,2 à × 2,7 ; en été, la convection domine et WRF redonne les valeurs de
  Prunay (× 0,6 à × 1).
- Règle de surface (EPA) : vent mesuré → surface au site de mesure ; vent simulé (MMIF) → surface de la maille du
  modèle. AERMET n'accepte
  un vent de référence qu'à ≥ 7 z0 : avec un vent à 10 m, z0 > 1,4 m n'est pas traitable.
- Le choix rural/urbain reste le premier facteur d'incertitude, devant la météo.
