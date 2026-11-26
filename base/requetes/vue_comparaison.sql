-- Vue : une ligne par station et par heure, avec mesure, météo et contribution modélisée (cas urbain)
CREATE OR REPLACE VIEW comparaison AS
SELECT m.station,
       m.debut_utc,
       max(m.valeur) FILTER (WHERE m.polluant = 'no2') AS no2_mesure,
       max(m.valeur) FILTER (WHERE m.polluant = 'nox') AS nox_mesure,
       max(mo.nox)                                       AS nox_modele,
       max(me.vitesse)                                   AS vitesse,
       max(me.direction)                                 AS direction,
       max(me.monin_obukhov)                             AS monin_obukhov
FROM mesures m
JOIN meteo  me ON me.debut_utc = m.debut_utc
JOIN modele mo ON mo.debut_utc = m.debut_utc AND mo.station = m.station AND mo.cas = 'urbain'
GROUP BY m.station, m.debut_utc;
