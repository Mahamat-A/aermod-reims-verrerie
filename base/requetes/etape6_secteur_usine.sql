-- Étape 6 en SQL : NOx mesuré et contribution modélisée quand le vent vient de l'usine (± 15°).
-- Reproduit exactement scripts/compare_secteurs.py (569 / 623 / 559 heures ; 19,9 / 46,1 / 9,7 µg/m³).
WITH usine AS (
    SELECT ST_SetSRID(ST_MakePoint(576601.2, 5453845.2), 32631) AS geom
),
direction_usine AS (            -- direction d'où doit venir le vent pour aller de l'usine à la station
    SELECT s.code, s.nom, round(degrees(ST_Azimuth(s.geom, u.geom)))::numeric AS d
    FROM stations s CROSS JOIN usine u
)
SELECT du.nom,
       du.d                              AS vent_de_usine,
       count(*)                          AS heures,
       round(avg(m.valeur)::numeric, 1)  AS nox_mesure,
       round(avg(mo.nox)::numeric, 2)    AS nox_modele_rural
FROM mesures m
JOIN meteo me           ON me.debut_utc = m.debut_utc
JOIN modele mo          ON mo.debut_utc = m.debut_utc AND mo.station = m.station AND mo.cas = 'rural'
JOIN direction_usine du ON du.code = m.station
WHERE m.polluant = 'nox'
  AND me.direction > 0                                              -- calmes exclus
  AND abs(mod((me.direction::numeric - du.d + 540), 360) - 180) <= 15
GROUP BY du.nom, du.d
ORDER BY du.d;
