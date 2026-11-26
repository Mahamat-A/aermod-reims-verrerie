# Étape 8 (suite) — Rural ou urbain : mesures, littérature, satellites, validation possible

État au 26/11/2026. Question : les mesures ou des observations indépendantes permettent-elles de choisir entre les
options rurale et urbaine d'AERMOD, premier facteur d'incertitude du projet ? Météo et rugosité : `etape8_wrf.md`.

## Expérience naturelle refaite (24/11) : test de sensibilité z0 = 0,25 m et écart de direction mesuré
AERMET 2024 Prunay avec z0 = 0,25 m toute l'année (`aermet/z0_025/`, hors convention : voir l'encadré de `etape8_wrf.md`),
AERMOD `aermod/reference_bati_z025/`.
Écart de direction WRF − Prunay en janvier (vent Prunay ≥ 1 m/s) : écart-type brut 46°, gonflé par 9,6 % d'heures
à plus de 90° ; **écart-type robuste 26°** (1,4826 × MAD). Comme cet écart contient aussi l'erreur propre de WRF,
l'erreur de direction de Prunay pour le panache est vraisemblablement de 20 à 30°.

| Modèle | σ = 0° | σ = 20° | σ = 30° | σ = 40° |
|---|---|---|---|---|
| rural z0 0,03 (Prunay) | β = −0,08 ± 0,65 (1,7 σ) | −0,39 ± 2,09 (0,7 σ) | −0,63 ± 5,30 (0,3 σ) | −0,47 ± 10,8 (0,1 σ) |
| rural z0 0,25 (sensibilité) | −0,08 ± 0,54 (2,0 σ) | −0,42 ± 1,73 (0,8 σ) | −0,75 ± 4,05 (0,4 σ) | −1,91 ± 7,75 (0,4 σ) |
| urbain | −0,16 ± 0,22 (5,4 σ) | −0,54 ± 0,71 (2,2 σ) | −1,23 ± 1,63 (1,4 σ) | −2,43 ± 3,14 (1,1 σ) |

(entre parenthèses : distance de β = 1 en écarts types ; pentes k z0 0,25 : 1,9 / 4,0 / 2,6 µg/m³ pour 1 000 t,
soit + 25 % par rapport à z0 0,03 avec le vent de Prunay.)

**Conclusion révisée.** Avec l'erreur de direction réaliste (20–30°), l'expérience naturelle ne contredit plus
l'option urbaine qu'à 1,4–2,2 σ : c'est une indication, pas une réfutation. Les deux options rurales restent
compatibles. Le test perd l'essentiel de sa puissance dès que la direction du panache est mal connue : pour
départager les options, il faudrait le vent au site (mât à l'usine, ou WRF validé) ou des mesures sous le panache.

## Ce que dit la littérature sur l'option urbaine près d'une usine (lu le 24/11)
**Paine, Warren & Moore (2016), Atmos. Environ. 129, 55–67, doi:10.1016/j.atmosenv.2016.01.003** (lu en entier,
PDF dans ~/Téléchargements ; étude financée par l'American Iron and Steel Institute).
- Idée : une grande installation industrielle qui dégage beaucoup de chaleur « diffuse » (non comptée dans les
  paramètres de cheminée) crée un **îlot de chaleur local** (« highly industrialized area », HIA) : la couche limite
  ne devient pas stable la nuit autour de l'usine, même en zone rurale. On le représente avec l'option urbaine
  d'AERMOD et une **population effective** déduite de l'excès de température ΔT (éq. 1 d'AERMOD :
  ΔT = 12 K × [0,1 ln(P/2 000 000) + 1]) ou du flux de chaleur anthropique Hu (ΔT ≈ Hu/4, Hu en W/m²).
- Seuils proposés : zone d'au moins **quelques centaines de mètres** de côté et **ΔT ≥ 8 K** (population effective
  ≈ 70 000) ; ΔT de 3–4 K est insuffisant. ΔT estimé par imagerie thermique satellite (ASTER, Landsat 8) ou par un
  bilan des pertes de chaleur.
- Cas étudié : aciéries de Gary et Hammond (Indiana), 99ᵉ centile du maximum journalier de SO₂ sur 1 h, capteurs à
  0,3 km et 1–4 km. Rural : 1 298 µg/m³ à Gary pour 175 mesurés (× 7,4), 290 à Hammond pour 96 (× 3,0) ; urbain
  population réelle 10 000 : 1 856 et 936 ; urbain population effective 1 000 000 : **392 et 179** (encore ≈ × 2).
  ΔT satellite d'été ≈ 11–12 K. Autre cas (LIFTOFF) : ~6 MW de chaleur diffuse sur 300 × 600 m, ΔT ≈ 8 K.
- Pour O-I : l'option urbaine utilisée ici (population de Reims 182 000) correspond à ΔT ≈ 9 K. Ce qu'il faudrait
  vérifier, c'est l'excès de température **de l'usine elle-même** (fours verriers ≈ 1 500 °C) : Landsat 8 (gratuit)
  ou un bilan des pertes thermiques. Si ΔT ≥ 8 K sur quelques centaines de mètres, l'option urbaine « HIA » serait
  justifiée **près de l'usine** — cohérent avec la forte turbulence de WRF à la maille de l'usine. Les stations, à
  3–7 km, et l'expérience naturelle (moyennes par secteur, non des pics horaires) portent sur une autre échelle :
  les deux résultats ne se contredisent pas forcément.

## Îlot de chaleur de l'usine vu par Landsat (24/11) — `scripts/landsat_usine.py`
Landsat 8/9, Collection 2 niveau 2 (température de surface ST_B10, 30 m rééchantillonné, résolution thermique
native 100 m), Microsoft Planetary Computer ; 43 scènes < 20 % de nuages (2022–2026), **32 retenues** avec une
fenêtre de 6 × 6 km claire à plus de 98 %. Anomalie = température de surface − médiane des champs (Corine 211,
231, 242, à plus de 1 km). Passage à 10 h 34 locale. Figure : `figures/etape8_landsat_usine.png`.

| Saison (scènes) | point chaud (max < 600 m) | moyenne 300 m autour du point chaud | ville (111/112) | surface > 4 K / > 8 K (r < 800 m) |
|---|---|---|---|---|
| hiver (2) | +6,7 K | +1,7 K | −0,3 K | 2,5 ha / 0 |
| automne (7) | +7,4 K | +2,3 K | +0,4 K | 8,0 ha / 0 |
| printemps (12) | +11,1 K | +5,6 K | +3,8 K | 55 ha / 7,5 ha |
| été (11) | +11,6 K | +5,2 K | +3,4 K | 44 ha / 7,2 ha |

- L'usine a une **signature thermique propre**, visible en hiver et en automne quand le reste de la ville ne
  ressort pas : point chaud à ≈ 150 m au nord-est de la cheminée (fours).
- Mais elle est **compacte et modérée** : en hiver, 2,5 ha au-dessus de +4 K, rien au-dessus de +8 K, +1,7 K en
  moyenne sur 300 m. Au printemps et en été, le soleil chauffe aussi les toits et les zones d'activité voisines
  (plus chaudes que l'usine à 2 km au sud et au sud-est) : on ne peut plus isoler la chaleur des procédés.
- **Critère de Paine et al. (2016) non atteint** (ΔT ≥ 8 K sur quelques centaines de mètres). Avec ΔT ≈ 2–4 K, la
  population effective serait de l'ordre de quelques milliers (insuffisant selon les auteurs). L'« îlot de chaleur
  industriel » ne justifie donc pas l'option urbaine ; il conforte plutôt l'option rurale (avec la surface de
  Prunay pour le vent mesuré).
- Limites : images de jour seulement (la nuit, l'écart serait probablement plus marqué ; ASTER a des images de
  nuit), 2 scènes d'hiver, température de surface et non de l'air, lissage par la résolution thermique de 100 m.

## Îlot de chaleur de l'usine vu par ASTER de nuit (24/11) — `scripts/aster_nuit_usine.py`
ASTER AST_08 v4 (température de surface, 90 m), NASA LP DAAC (compte Earthdata de l'auteur, jeton local) ;
40 scènes de nuit sur l'usine (≈ 22 h 30 locale, 2006–2024), 11 avec ≤ 5 % de nuages (estimation AST_L1T),
**9 valides** (2 écartées : valeurs de remplissage). Même méthode que Landsat (anomalie / médiane des champs).
Figure : `figures/etape8_aster_nuit_usine.png`.

| Nuit | T des champs | max < 600 m | moy. 300 m (point chaud de jour) | ville (111/112) | > 4 K / > 8 K |
|---|---|---|---|---|---|
| 19/11/2006 | 4,4 °C | +1,3 K | −0,2 K | +0,6 K | 0 / 0 |
| 09/07/2016 | 19,4 °C | +5,4 K | +2,1 K | +3,4 K | 22,7 / 0,8 ha |
| 16/10/2017 | 14,5 °C | +3,4 K | +0,7 K | +0,9 K | 0 / 0 |
| 01/09/2018 | 12,6 °C | +4,0 K | +1,3 K | +2,0 K | 3,2 / 0 |
| 15/05/2019 | 8,9 °C | +3,8 K | +1,0 K | +2,6 K | 4,1 / 0 |
| 26/08/2019 | 19,7 °C | +4,8 K | +2,0 K | +2,7 K | 13,0 / 0 |
| 31/08/2021 | 13,5 °C | +3,3 K | +1,2 K | +1,9 K | 0 / 0 |
| 01/07/2022 | 13,7 °C | +4,1 K | +1,5 K | +2,0 K | 3,2 / 0 |
| 27/02/2023 | −1,0 °C | +1,4 K | −0,7 K | +0,5 K | 0 / 0 |

Moyenne des 9 nuits : maximum à moins de 600 m de +2,7 K (à 435 m à l'ouest, hors du point chaud de jour),
+1,2 K en moyenne dans 300 m autour de la cheminée, **aucun pixel au-dessus de +4 K**.

- La nuit, **l'usine ne se distingue pas du tissu urbain** : son excès (+1 K environ) est même un peu inférieur à
  celui de la ville (+0,5 à +3,4 K selon les nuits). Le point chaud de jour (fours, toits) ne laisse pas de trace
  nocturne nette à 90 m de résolution.
- Le **critère de Paine et al. (2016) n'est clairement pas atteint** (ΔT ≥ 8 K sur quelques centaines de mètres).
  Jour (Landsat) et nuit (ASTER) concordent : pas d'« îlot de chaleur industriel » qui justifierait l'option urbaine.
- Limites : température de surface (pas de l'air), 9 nuits, résolution 90 m, nuits d'été surreprésentées.

## Confrontation horaire aux mesures (26/11)
`scripts/correlation_mesures.py`, résultats `rapport/etape8_correlation_mesures.csv`.
Régression NOx mesuré = β × NOx modélisé de l'usine + effets heure du jour + classes de vent WRF ; β = 1 si le
modèle est juste ; incertitude par rééchantillonnage de jours entiers. 7 cas × 3 stations × 2 mois = 42 régressions.
- **Corrélation brute trompeuse** : sans contrôle, le rang de corrélation vaut −0,3 à −0,4 en rural et +0,3 à +0,4 en
  urbain (janvier). Le signe dépend de l'option, pas de l'usine : en rural, le panache touche les stations par vent
  soutenu, quand l'air urbain est propre ; en urbain, il les touche par temps calme et stable, quand le NOx du trafic
  s'accumule. Une corrélation brute ne prouve donc rien ici.
- **Avec contrôles, β n'est pas mesurable** : écarts types de 0,45 à 24 (le signal de l'usine, 0,3–4,6 µg/m³ au 99e
  centile horaire, est noyé dans des variations horaires de 5 à 63 µg/m³). β est compatible à la fois avec 0 et avec 1
  dans presque tous les cas ; les quelques écarts à 2–2,4 σ (Doumer en juillet avec WRF rural, β ≈ 27 ; Bétheny en
  juillet avec Prunay urbain, β ≈ −0,6) vont dans les deux sens et sont attendus par hasard sur 42 tests : ils
  traduisent une météo commune mal contrôlée, pas l'usine.
- **Aucune valeur de z0 n'est favorisée** par les mesures : β est le même à z0 1 m et 2 m. Les stations, à 2,5–5,6 km
  et loin sous le seuil de détection, ne peuvent pas trancher ; seules des mesures horaires sous le panache le pourraient.

## Faisabilité d'une validation par la mesure (24/11) — `scripts/tubes_faisabilite.py`
Récepteurs virtuels à 0,5–2 km au NE (sous le vent dominant) et au SO (témoins), AERMOD horaire 2024, moyennes
de 14 jours (exposition d'un tube passif), NO₂ = 0,9 × NOx.
- Rural z0 0,25 (vent de Prunay, test de sensibilité, donc plutôt haut) : à 0,5–1 km NE, médiane 0,21–0,25 µg/m³, maximum 0,7–0,8 ; différence NE − SO ≈ +0,1 à +0,2.
- Urbain : valeurs presque identiques (0,18–0,23 ; max 0,6–0,7) → même une mesure parfaite sur 14 jours ne
  départagerait pas les options à ces distances.
- Un tube NO₂ a une incertitude de l'ordre de 15–25 % sur un fond urbain de 15–20 µg/m³ (± 3–4 µg/m³), sans
  compter l'effet des routes proches : **le signal de l'usine est 10 à 20 fois plus petit que le bruit. Les tubes
  passifs NO₂ sont exclus** (correction de la recommandation antérieure).
- SO₂ : fond urbain faible, meilleur traceur ; mais flux d'O-I inconnu (IREP 2024 « < seuil », soit < 150 t/an ;
  arrêté : 28 à 85 kg/h au maximum ; mesure en continu à la cheminée depuis ≈ 2024 d'après l'inspection de 2025).
- Pas de surveillance environnementale de l'air autour du site actuellement (inspection 2025, constat n° 7) ;
  une étude de risques sanitaires (v2, 11/02/2025) a été remise à l'inspection, non publique.
- Ce qui pourrait trancher : analyseurs horaires (NOx par chimiluminescence, SO₂ par fluorescence UV) et
  anémomètre sur place, à 0,5–1 km au NE, 2–3 mois, en triant les heures selon la direction du vent mesurée ;
  et les émissions horaires réelles de la cheminée (demande à la DREAL, droit d'accès à l'information
  environnementale).

## Conclusion (rural ou urbain)
- Les mesures défavorisent l'option urbaine aux stations sans la réfuter (1,1–2,2 σ avec une erreur de direction
  réaliste de 20–40°) ; l'option rurale est compatible.
- L'usine n'a pas d'« îlot de chaleur industriel » au sens de Paine et al. (2016) : Landsat (jour) et ASTER (nuit)
  donnent quelques kelvins au plus, loin des 8 K requis.
- Les stations, à 2,5–5,6 km, ne peuvent pas trancher (signal 10 à 100 fois sous le bruit, à l'heure comme à l'année) ;
  seules des mesures horaires sous le panache, à 0,5–1 km au nord-est, le pourraient.
- Résultats donnés en fourchette : rural (référence) – urbain (borne haute).
