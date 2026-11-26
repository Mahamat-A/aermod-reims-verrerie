# Étape 6 — Comparaison modèle–mesures (NO₂, Reims, 2024)

Brouillon de synthèse, 22/11/2026. Figures : `figures/etape6_secteurs_no2.png`,
`figures/aermod_reference_2024_annuel.png`, `figures/aermod_reference_2024_max1h.png`.

## Données
- **Mesures** : moyennes horaires validées LCSQA (fichiers E2) d'ATMO Grand Est, 2024, stations
  Jean d'Aulan (FR14012, fond urbain), Doumer (FR14011, trafic), Bétheny (FR14010, fond périurbain).
  Couverture 91–97 %. Heures en UTC (vérifié sur le pic de NO du trafic du matin).
- **Modèle** : AERMOD 26135, cas de référence avec bâtiments (`aermod/reference_bati`), puis NO₂ par
  OLM (ozone horaire mesuré à Jean d'Aulan, complété par Bétheny ; NO₂/NOx à l'émission 0,10) et ARM2.
- **Vent** : Reims-Prunay (fichier AERMET), heures alignées (mesure UTC début d'heure → AERMOD heure
  locale standard de fin, + 2 h).

## Conversion NOx → NO₂
OLM et ARM2 donnent exactement le même résultat, NO₂ = 0,90 × NOx à toutes les heures : l'ozone
(52 µg/m³ en moyenne) est toujours en large excès devant le NOx de l'usine (quelques µg/m³ au plus),
et les deux méthodes plafonnent alors au rapport d'équilibre par défaut de 0,9. Le choix de la
méthode n'a donc pas d'importance ici.

## Résultats
| Station | Vent venant de l'usine | NO₂ mesuré dans ce secteur | Contribution modélisée (NO₂) | Part |
|---|---|---|---|---|
| Jean d'Aulan | 67° (ENE) | 13,9 µg/m³ | 0,28 µg/m³ | 2 % |
| Doumer | 133° (SE) | 22,5 µg/m³ | 0,51 µg/m³ | 2 % |
| Bétheny | 178° (S) | 8,1 µg/m³ | 0,34 µg/m³ | 4 % |

Moyennes annuelles modélisées aux stations : 0,027 à 0,050 µg/m³ de NO₂, pour 9,3 (fonds) et
23,3 µg/m³ (Doumer) mesurés, soit moins de 0,5 %.

## Interprétation
1. **Le modèle place bien l'influence de l'usine** : pic étroit (± 15°) exactement dans la direction
   géométrique de la verrerie pour chaque station ; 1,7 à 3 % des heures font 65 à 80 % de la moyenne.
2. **Les mesures ne montrent pas ce pic.** Les variations du NO₂ mesuré avec la direction du vent
   (facteur 2 à 3) sont dominées par d'autres causes :
   - les vents de NE à E (0–100°) donnent le NO₂ le plus élevé **aux trois stations à la fois**, y
     compris là où l'usine n'est pas dans cette direction (Bétheny, Doumer) : ce sont les situations
     anticycloniques continentales, froides et stables, qui accumulent toutes les émissions urbaines ;
   - les vents de SO à O (200–260°), océaniques et ventés, donnent le NO₂ le plus bas ;
   - le maximum de Jean d'Aulan vers 60–80° coïncide avec la direction de l'usine, mais il est présent
     aussi à Bétheny et à Doumer : il est **météorologique**, pas dû à la verrerie.
3. **Seuil de détection** : sur les heures « vent de l'usine », la moyenne mesurée n'est connue qu'à
   ± 2 à 10 µg/m³ près (2σ ; autocorrélation horaire 0,83–0,86, soit ~50 heures indépendantes).
   Le signal attendu (0,3–0,5 µg/m³) est 6 à 30 fois plus petit.

## Conclusion
Les mesures et le modèle sont **cohérents** : AERMOD prédit une contribution de la verrerie
inférieure au seuil de détection des stations, et les stations ne montrent aucun excès attribuable
à l'usine. Le réseau, conçu pour l'exposition urbaine (trafic, fond), ne permet **ni de valider ni
d'invalider** quantitativement le modèle pour cette source. C'est un résultat en soi : la verrerie
pèse moins de 0,5 % du NO₂ moyen mesuré et environ 2 à 4 % du NO₂ mesuré lorsque le vent souffle de
l'usine vers une station.

## Ce qui permettrait une vraie validation
- un point de mesure **sous le vent dominant** (NE, 0,5–1 km, ou sur le Mont de Berru), par exemple
  des tubes passifs NO₂ sur une campagne ;
- un traceur propre à l'usine (le SO₂ est sous le seuil de déclaration en 2024) ;
- la comparaison aux concentrations à la cheminée, si l'autosurveillance de l'exploitant était
  publique (débits horaires réels au lieu de la répartition mensuelle).

## Limites (→ étape 7)
Émissions mensuelles reconstruites (et non horaires), position A/B et diamètre de la cheminée,
température des fumées, option urbaine, météo de Prunay à 7 km, hauteurs BD TOPO.

## Mise à jour après le choix urbain (étape 7)
Le cas de référence est désormais urbain. Par vent venant de l'usine, la contribution modélisée
(NO₂, OLM) devient 1,57 µg/m³ à Jean d'Aulan, 1,18 à Doumer et 0,65 à Bétheny (5 à 11 % du NO₂
mesuré dans ce secteur), soit 4 à 8 fois moins que l'incertitude des moyennes mesurées : la
conclusion ne change pas. La figure `etape6_secteurs_no2.png` a été refaite avec ce cas.

## Recherche de mesures de validation existantes (23/11/2026)
**Aucune campagne de mesure publique autour de l'usine n'a été trouvée.**
- ATMO Grand Est : pas de campagne de tubes passifs publiée autour de la verrerie ou de la zone
  industrielle ; seules les 3 stations fixes existent.
- Exploitant : l'arrêté de 2005 (art. 19) prévoit une surveillance de l'air autour du site
  (Coureaux, Cerisaie, CRNA), mais pour les **métaux** seulement, et elle n'est pas réalisée
  (inspection du 19/08/2025). L'étude de risque sanitaire (ERS) de l'exploitant (v2 du 11/02/2025)
  et l'interprétation de l'état des milieux (IEM), prescrite par l'arrêté du 08/07/2025 et attendue
  au 1er semestre 2026, **ne sont pas publiques** : on ne connaît que leurs conclusions résumées dans
  le rapport d'inspection du 28/04/2025 (QD cumulé 0,746, porté par l'arsenic ; ERI 0,95·10⁻⁵).
  Ces documents relèvent de l'information environnementale et peuvent être demandés à la DREAL
  (UD de la Marne).

**Comparaison avec un autre modèle (ATMO Grand Est).** Pour la révision du PPA, ATMO a simulé la
suppression de 100 % des émissions industrielles du Grand Reims (1 103 t de NOx en 2018, dont
≈ 440 t pour O-I) : la moyenne annuelle de NO₂ baisse **au plus de 2 µg/m³** (comité local de l'air
du 10/12/2020). Notre cas de référence, ramené aux émissions 2018 d'O-I (440/143 = ×3,1), donne
un maximum annuel de 0,25 × 3,1 ≈ **0,8 µg/m³** de NO₂ pour la seule verrerie, soit environ 40 % de
la baisse simulée par ATMO pour toute l'industrie, la part d'O-I dans les émissions industrielles.
Les deux modèles, indépendants, donnent le **même ordre de grandeur**. Réserves : valeur ATMO
arrondie, autres sources industrielles (positions et hauteurs inconnues), météo 2018.

**Une piste de vraie validation avec les données existantes : l'expérience naturelle.**
Les émissions de l'usine ont fortement varié : ≈ 440 t (2018), −40 % après le DeNOx catalytique de
septembre 2019, puis 384 t (2022), 275 t (2023) et 143 t (2024). Si le modèle est juste, le NO₂
mesuré **par vent venant de l'usine** doit baisser davantage que par les autres vents, d'un écart
prévisible : en 2022 la contribution dans ce secteur serait ≈ 2,7 fois celle de 2024, soit 1,7 à
4,2 µg/m³, et l'écart 2022–2024 de 1,1 à 2,6 µg/m³. Comparer secteur usine et autres secteurs
(« différence de différences ») élimine les tendances communes (trafic, météo). Le signal reste
proche du bruit, mais en cumulant plusieurs années et les trois stations il devient testable.
Données nécessaires : LCSQA 2018–2024 et météo de Prunay des mêmes années.

**Ordre de grandeur des émissions horaires.** Le rapport d'inspection du 28/04/2025 indique un flux
de NO₂ de 59,8 kg/h pour le seul four 2 en juin 2024, au-dessus du flux réglementaire total de
45 kg/h, et 629 h d'indisponibilité du traitement des fumées en 2023. Notre modèle utilise
21,7 kg/h (moyenne de janvier à juin reconstituée depuis le total annuel) : les **maxima horaires**
modélisés peuvent donc être sous-estimés d'un facteur 2 à 3 lors des dysfonctionnements ; les
moyennes annuelles, calées sur le total déclaré, ne le sont pas.

Sources : rapport d'inspection DREAL du 28/04/2025 et du 19/08/2025 (`donnees/OI_France_Reims/documents/`),
compte rendu et présentation du comité local de l'air PPA de Reims du 10/12/2020
(grand-est.developpement-durable.gouv.fr).

## Résultat de l'expérience naturelle 2013–2025 (23/11/2026)
Script : `scripts/experience_naturelle.py` ; tableau : `observations/experience_naturelle.csv` ;
figure : `figures/etape6_experience_naturelle.png`.

**Données.**
- NO₂ horaire validé de l'AEE (e-reporting E1a), 2013–2025, pour les 3 stations. Les heures de
  l'AEE sont en UTC+1 : une fois décalées d'une heure, elles sont identiques à 100 % aux fichiers
  LCSQA de 2024.
- Vent horaire de Météo-France à Reims-Prunay (direction arrondie à 10°).
- Émissions IREP d'O-I : 343, 343, 450, 566, 517, 437, 275 t (2013–2019) ; 2020 non déclarée,
  donc exclue ; 361, 384, 275, 143, 250 t (2021–2025).
- Doumer 2013 est exclu (station ouverte en cours d'année).

**Méthode.**
- Pour chaque station et chaque année : D = NO₂ moyen par vent venant de l'usine (± 15°, vent
  ≥ 1 m/s), moins le NO₂ moyen des secteurs voisins (15 à 45°). Environ 530 h par an dans le
  secteur de l'usine ; écart type de D de 0,6 à 1,2 µg/m³, par rééchantillonnage de jours entiers.
- La pente modélisée k est le même D calculé avec les sorties horaires AERMOD de 2024
  (NO₂ = 0,9 NOx), divisé par 143 t.
- Ajustement pondéré : D = a + b·(année − 2019) + β·k·E, avec une ordonnée et une tendance propres
  à chaque station. β = 1 signifie que le modèle est juste, β = 0 qu'aucun effet n'est visible.

**Résultats.**
| Écart de direction supposé entre Prunay et le panache | Option urbaine (k JdA = 9,2 µg/m³ pour 1 000 t) | Option rurale (k JdA = 1,5) |
|---|---|---|
| 0° | β = −0,16 ± 0,22 ; β = 1 exclu à 5,4 σ | β = −0,08 ± 0,65 ; β = 1 à 1,7 σ |
| 10° | β = −0,23 ± 0,31 ; exclu à 4,0 σ | β = −0,14 ± 0,92 ; à 1,2 σ |
| 20° | β = −0,54 ± 0,71 ; exclu à 2,2 σ | β = −0,39 ± 2,09 ; à 0,7 σ |

Le χ² réduit vaut 0,85, donc les écarts types estimés sont réalistes.

**Lecture.**
1. Les émissions ont varié d'un facteur 4, mais **le NO₂ par vent venant de l'usine ne les suit
   pas de façon détectable**.
2. L'option urbaine prévoit, à Jean d'Aulan, un excès qui passe de 1,3 µg/m³ (143 t) à
   5,2 µg/m³ (566 t). Un tel signal serait visible, or il n'apparaît dans aucune année. **Les
   mesures contredisent l'ampleur de la contribution que prévoit l'option urbaine aux stations.**
3. L'option rurale prévoit 2 à 6 fois moins selon la station : elle est compatible avec les mesures, mais celles-ci
   ne peuvent pas la confirmer (signal sous le bruit).

> **Mise à jour du 24–26/11/2026.** L'écart de direction mesuré entre WRF (maille de l'usine) et Prunay est de
> 26° en janvier et 38° en juillet (écart type robuste). Avec 20–40°, l'option urbaine n'est plus défavorisée qu'à
> 1,1–2,2 σ : les mesures la **défavorisent sans la réfuter**. Voir `etape8_rural_urbain.md`.

**Réserves.**
- **Représentativité de la direction du vent.** Le panache suit le vent local, alors que le tri
  des heures utilise Prunay, à 7 km. Entre Prunay et les stations voisines à 25 km (Mourmelon,
  Chouilly), l'écart médian est de 10° par vent ≥ 2 m/s et de 20° par vent faible. Le tableau
  encadre cet effet : jusqu'à 20°, l'option urbaine reste défavorisée. Au-delà de 30°, le test ne
  conclut plus.
- **Méthode de la pente modélisée.** Elle est calculée avec la météo de 2024 seule, et les
  émissions sont annuelles (répartition intra-annuelle inconnue). Les paramètres de rejet avant
  le DeNOx de 2019 (température, débit) peuvent avoir été différents.
- **Secteurs témoins.** Ils peuvent recevoir une partie du panache réel, ce qui réduit D ; cet
  effet est inclus dans le test d'écart de direction.
- **Option rurale.** Ce résultat ne valide pas l'option rurale : il montre seulement que l'option
  urbaine surestime la contribution aux stations, dans les conditions de ce test.

**Prochaine étape.** Les sorties WRF à 1 km de l'étape 8 permettront de mesurer l'écart réel entre
la direction du vent à Prunay et celle à l'usine, donc de resserrer ce test.
