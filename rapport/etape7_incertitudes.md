# Étape 7 — Incertitudes et sensibilité (NOx de la verrerie O-I, 2024)

Brouillon de synthèse, 22/11/2026. Figure : `figures/etape7_sensibilite.png`.
Calculs : `scripts/sensibilite.py` (une copie du cas `aermod/reference_bati` par variante, un seul
paramètre modifié ; débit volumique réel conservé quand T ou D changent).

## Résultats

| Variante | Max annuel (grille) | Max horaire (grille) | Moyenne aux 3 stations |
|---|---|---|---|
| Référence | 0,218 µg/m³ | 49,2 µg/m³ | 0,039 µg/m³ |
| **Option urbaine (182 000 hab.)** | **+30 %** | **−72 %** | **+181 %** (Jean d'Aulan +357 %) |
| Fumées à 200 °C | +18 % | +14 % | +11 % |
| Fumées à 300 °C | −13 % | −11 % | −8 % |
| Diamètre 1,5 m (22 m/s) | −7 % | 0 % | −2 % |
| Juillet heure par heure | 0 % | 0 % | −2 % |
| Cheminée en position B | 0 % | −1 % | +1 % |
| Sans les bâtiments | 0 % | 0 % | 0 % |

## Lecture
1. **Le choix rural/urbain domine tout le reste.** L'option urbaine d'AERMOD ajoute, la nuit, le
   mélange dû à l'îlot de chaleur de la ville : le panache, qui restait en altitude en atmosphère
   stable, est ramené vers le sol près de l'usine (stations ×2 à ×4,6). À l'inverse, ce mélange
   empêche le panache stable d'atteindre intact le Mont de Berru : le maximum horaire chute de 72 %.
2. **La température des fumées** vient ensuite (±10 à 20 % pour ±50 °C) : c'est la flottabilité,
   comme prévu à l'étape 1.
3. **Diamètre, position A/B, bâtiments, découpage de juillet : moins de 7 %.** Les incertitudes qui
   ont demandé le plus de travail de terrain (triangulation, BD TOPO) pèsent peu : utile pour savoir
   où ne plus investir de temps.

## Le choix rural ou urbain
La règle de l'EPA (méthode d'Auer) : option urbaine si plus de 50 % de l'occupation du sol dans un
rayon de 3 km autour de la source est de type urbain (industrie, commerce, habitat dense). La
verrerie est en pleine ville, mais le cercle de 3 km inclut aussi des champs à l'est et au sud.
**À trancher par un calcul d'occupation du sol (BD TOPO ou Corine Land Cover)** ; en attendant,
le résultat est donné sous forme de fourchette rural–urbain.

## Incertitudes non simulées
- **Émissions totales** (143 t déclarées) : les concentrations sont proportionnelles au débit ;
  une erreur de ±20 % sur la déclaration donne ±20 % partout.
- **Répartition dans le temps** : pics de démarrage et panne du DéNOx de juillet 2024 ignorés ;
  arrêt du four 2 non daté.
- **Météorologie** : Reims-Prunay à ~10 km de l'usine, en campagne ; rugosité de l'aérodrome et non
  de la ville. → étape 8 (WRF à l'emplacement de l'usine).
- **Modèle** : l'EPA considère qu'AERMOD prédit les maxima à un facteur 2 près environ.

## Conclusion
Même dans l'hypothèse la plus pénalisante (urbaine), la contribution moyenne de la verrerie aux
stations reste inférieure à 0,15 µg/m³, soit moins de 2 % du NO₂ mesuré : **la conclusion de
l'étape 6 ne change pas**. En revanche, la carte des zones les plus touchées (centre-est de Reims ou
Mont de Berru) dépend du choix rural/urbain, qu'il faut justifier.

## Décision rural / urbain (22/11/2026) → **urbain**
Calcul : `scripts/rural_urbain.py` (Corine Land Cover 2018, cercle de 3 km) et densité de population
d'après la BD TOPO (nombre de logements des bâtiments du cercle).

| Critère | Valeur | Seuil EPA | Verdict |
|---|---|---|---|
| Auer, urbain certain (111, 121, 122) | 23,8 % | > 50 % | rural |
| Auer, en comptant le tissu urbain discontinu (112) | 69,6 % | > 50 % | urbain |
| Densité de population (45 700 logements × 1,9–2,1) | ≈ 3 000–3 400 hab/km² | > 750 hab/km² | **urbain** (×4) |

La méthode d'Auer est indécise : tout dépend du classement du tissu urbain discontinu (46 % du
cercle). La densité de population, critère alternatif admis par l'EPA, tranche nettement. Le tissu
« discontinu » de Reims (immeubles et pavillons serrés) se comporte donc comme de l'habitat compact.
**Cas de référence final : `aermod/reference_urbaine`** (option urbaine, 182 000 hab., bâtiments).
Le cas rural reste un test de sensibilité.

Effet sur l'étape 6 : contribution de la verrerie (NO₂, OLM) par vent venant de l'usine
0,65 à 1,57 µg/m³ (5 à 11 % du NO₂ mesuré dans ce secteur) ; moyenne annuelle 0,05 à 0,13 µg/m³
(0,5 à 1,4 %). Toujours sous le seuil de détection (± 2 à 10 µg/m³) : conclusion inchangée.

## Remise en question par les mesures (23/11/2026)
L'expérience naturelle 2013–2025 (voir `etape6_comparaison.md`, dernière section) montre que le NO₂
mesuré par vent venant de l'usine ne suit pas les variations des émissions (facteur 4). L'option
urbaine prévoit aux stations une contribution que les mesures excluent, à 2,2–5,4 σ selon l'écart de
direction du vent supposé. L'option rurale reste compatible. Le critère de l'EPA (densité de
population) désigne l'option urbaine, mais **les observations indiquent qu'elle surestime la
contribution aux stations**. Décision à reprendre : présenter les résultats comme une fourchette
rurale–urbaine, ou revenir au cas rural en justifiant l'écart au critère de l'EPA par les mesures.

> **Mise à jour du 24–26/11/2026.** L'écart de direction mesuré entre WRF (maille de l'usine) et Prunay est de
> 26° en janvier et 38° en juillet (écart type robuste). Avec 20–40°, l'option urbaine n'est plus défavorisée qu'à
> 1,1–2,2 σ : les mesures la **défavorisent sans la réfuter**. Voir `etape8_rural_urbain.md`.

**Décision du 23/11/2026 : fourchette rurale–urbaine.** Les deux cas sont conservés comme cas de
référence (`aermod/reference_bati` en rural, `aermod/reference_urbaine` en urbain). Chaque résultat
est donné en deux valeurs ; l'évaluation sanitaire retient, pour chaque durée, la plus forte des
deux options (vue SQL `sensibles_enveloppe`). L'étape 8 (WRF → MMIF) sera faite pour les deux options.
