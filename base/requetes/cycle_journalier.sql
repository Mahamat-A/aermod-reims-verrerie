-- À quelle heure (locale d'hiver = UTC+1) la verrerie pèse-t-elle le plus aux stations ?
SELECT extract(hour FROM debut_utc + interval '1 hour')          AS heure_locale,
       round(avg(nox_modele)::numeric, 3)                          AS nox_usine,
       round(avg(nox_mesure)::numeric, 1)                          AS nox_mesure,
       round((100 * avg(nox_modele) / avg(nox_mesure))::numeric, 2) AS part_pct,
       round((100 * avg((monin_obukhov < 0)::int))::numeric)       AS pct_instable
FROM comparaison
WHERE nox_mesure IS NOT NULL
GROUP BY 1
ORDER BY 1;
