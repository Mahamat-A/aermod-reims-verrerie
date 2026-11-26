# Volet risques sanitaires — NO₂ de la verrerie O-I aux établissements sensibles (2024)

Brouillon, 22/11/2026. Démarche inspirée du guide INERIS « Évaluation de l'état des milieux et des
risques sanitaires » (2ᵉ éd., 2021), limitée ici au NO₂ par inhalation (seul polluant déclaré par
l'exploitant au-dessus des seuils IREP en 2024).

## Méthode
1. **Cibles** : 173 établissements sensibles à moins de 4 km de la cheminée, d'après la BD TOPO
   (« zones d'activité ou d'intérêt ») : 95 écoles, 15 collèges, 17 lycées, 21 hôpitaux,
   16 maisons de retraite, 9 structures d'accueil de personnes handicapées
   (`scripts/points_sensibles.py`). Le plus proche : école maternelle Jules Ferry, à 430 m.
2. **Concentrations** : AERMOD, cas de référence (option urbaine, bâtiments, émissions 2024
   déclarées et modulées), NO₂ par OLM avec l'ozone mesuré, en chaque établissement
   (altitude AERMAP) : moyenne annuelle, maximum sur 24 h, maximum horaire (`aermod/sensibles/`).
3. **Valeurs de comparaison** : valeurs guides de l'OMS (2021) pour le NO₂ — 10 µg/m³ (annuel),
   25 µg/m³ (24 h), 200 µg/m³ (1 h) ; valeur limite européenne 40 µg/m³ (20 µg/m³ en 2030).
   Le NO₂ n'a pas de valeur toxicologique de référence au sens strict : on calcule un
   **quotient de danger (QD) = concentration / valeur guide OMS**, en le présentant comme tel.
4. **Exposition totale** : contribution de l'usine + fond urbain mesuré à Jean d'Aulan
   (9,3 µg/m³ en 2024). Calculs SQL : `base/requetes/risques_sanitaires.sql`.

## Résultats
| Type | Nombre | NO₂ annuel (usine), max | Max 24 h | Max 1 h | QD annuel (usine) |
|---|---|---|---|---|---|
| Écoles | 95 | 0,19 µg/m³ | 1,9 µg/m³ | 9,9 µg/m³ | 0,019 |
| Collèges | 15 | 0,19 | 2,1 | 9,7 | 0,019 |
| Hôpitaux | 21 | 0,19 | 1,7 | 7,6 | 0,019 |
| Maisons de retraite | 16 | 0,18 | 1,5 | 10,4 | 0,018 |
| Lycées | 17 | 0,18 | 1,6 | 7,6 | 0,018 |
| Accueil handicap | 9 | 0,15 | 1,5 | 9,3 | 0,015 |

Établissements les plus exposés : écoles Docteur Roux, Saint-Louis et Barthou (1,5–2 km),
0,19 µg/m³ dus à l'usine, soit 2 % d'une exposition totale de 9,5 µg/m³.

## Interprétation
- **La contribution de la verrerie est faible** : QD ≤ 0,02 en moyenne annuelle (50 fois sous la
  valeur guide), maximum sur 24 h ≤ 2,1 µg/m³ (12 fois sous 25), maximum horaire ≤ 10,4 µg/m³
  (20 fois sous 200). Les maxima sur 24 h et 1 h sont des valeurs maximales de l'année, plus
  sévères que les percentiles sur lesquels reposent les valeurs OMS : la comparaison est prudente.
- **L'exposition totale est proche de la valeur guide annuelle de l'OMS** (QD ≈ 0,95 en fond
  urbain), à cause du fond urbain et non de l'usine. Près des axes routiers, le NO₂ mesuré
  (23 µg/m³ à Doumer) dépasse la valeur guide : l'enjeu sanitaire du NO₂ à Reims est le trafic.
- Les établissements les plus exposés à l'usine ne sont pas les plus proches (430 m) mais ceux
  situés à 1,5–2 km, là où le panache urbain retombe : la distance seule ne suffit pas à
  hiérarchiser les cibles.

## Limites
- NO₂ seul ; les particules et les métaux de l'usine (four verrier) ne sont pas déclarés au-dessus
  des seuils IREP et n'ont pas été modélisés.
- Émissions déclarées (réalistes), et non aux valeurs limites autorisées comme dans une étude
  réglementaire ; avec la valeur limite annuelle de l'arrêté (399 t/an au lieu de 143 t),
  les concentrations seraient multipliées par 2,8, soit un QD usine ≈ 0,05 : la conclusion ne change pas.
- Fond urbain pris à une seule station (Jean d'Aulan) pour tous les établissements.

## Fourchette rurale–urbaine (23/11/2026)
Les mesures 2013–2025 défavorisent l'option urbaine aux stations sans la réfuter (`etape6_comparaison.md`,
`etape8_rural_urbain.md`), mais la
densité de population de l'EPA la désigne : les deux options sont donc gardées. Le rural a été calculé
aux mêmes établissements (`aermod/sensibles_rural`, `scripts/sensibles_fourchette.py`). Pour chaque
durée, l'évaluation retient **l'enveloppe**, c'est-à-dire la plus forte des deux options (vue SQL
`sensibles_enveloppe`, fonction GREATEST).

| Type | Nombre | Annuel, rural – urbain (µg/m³) | Max 24 h, rural – urbain | Max 1 h, rural – urbain | QD annuel (enveloppe) | QD 1 h (enveloppe) |
|---|---|---|---|---|---|---|
| Écoles | 95 | 0,100 – 0,194 | 1,85 – 1,86 | 11,0 – 9,9 | 0,019 | 0,055 |
| Collèges | 15 | 0,102 – 0,187 | 2,10 – 2,11 | 9,9 – 9,7 | 0,019 | 0,050 |
| Hôpitaux | 21 | 0,064 – 0,186 | 0,91 – 1,65 | 9,4 – 7,6 | 0,019 | 0,047 |
| Maisons de retraite | 16 | 0,075 – 0,183 | 1,19 – 1,50 | 10,3 – 10,4 | 0,018 | 0,052 |
| Lycées | 17 | 0,081 – 0,183 | 1,47 – 1,59 | 10,2 – 7,6 | 0,018 | 0,051 |
| Accueil handicap | 9 | 0,056 – 0,153 | 1,45 – 1,52 | 6,8 – 9,3 | 0,015 | 0,046 |

L'option urbaine domine la moyenne annuelle (×1,9 à ×2,9). Les maxima sur 24 h et 1 h sont proches
dans les deux options aux établissements : le maximum horaire rural de 49 µg/m³ de NOx tombe sur le
Mont de Berru, sans établissement sensible. **Conclusion inchangée** : QD ≤ 0,02 en annuel et ≤ 0,06
sur 1 h pour la seule verrerie ; l'enjeu reste le fond urbain et le trafic.
