-- Volet risques sanitaires : NO2 dû à la verrerie aux établissements sensibles (OLM),
-- options rurale ET urbaine d'AERMOD (fourchette décidée le 23/11/2026, voir rapport/etape7_incertitudes.md).
-- Valeurs de comparaison : OMS 2021 (annuel 10 µg/m³ ; 24 h 25 µg/m³ ; 1 h 200 µg/m³),
-- valeur limite UE actuelle 40 µg/m³ (annuel), 20 µg/m³ en 2030 ; fond mesuré à Jean d'Aulan.
-- Données : base/sensibles.csv (scripts/sensibles_fourchette.py). Lancer depuis base/ :
--   psql oi_reims -P pager=off -f requetes/risques_sanitaires.sql
DROP VIEW IF EXISTS sensibles_enveloppe;
DROP TABLE IF EXISTS sensibles;
CREATE TABLE sensibles (
    id text PRIMARY KEY, type text, nom text, distance_m real,
    no2_annuel_urbain real, no2_max24h_urbain real, no2_max1h_urbain real,
    no2_annuel_rural  real, no2_max24h_rural  real, no2_max1h_rural  real,
    geom geometry(Point, 32631)
);
CREATE TEMP TABLE sensibles_brut (id text, type text, nom text, distance_m real, x float8, y float8,
    no2_annuel_urbain real, no2_max24h_urbain real, no2_max1h_urbain real,
    no2_annuel_rural real, no2_max24h_rural real, no2_max1h_rural real);
\copy sensibles_brut FROM 'sensibles.csv' WITH (FORMAT csv, HEADER true)
INSERT INTO sensibles
SELECT id, type, nom, distance_m,
       no2_annuel_urbain, no2_max24h_urbain, no2_max1h_urbain,
       no2_annuel_rural, no2_max24h_rural, no2_max1h_rural,
       ST_SetSRID(ST_MakePoint(x, y), 32631) FROM sensibles_brut;

-- Enveloppe : pour chaque établissement et chaque durée, la plus forte des deux options (GREATEST).
CREATE OR REPLACE VIEW sensibles_enveloppe AS
SELECT id, type, nom, distance_m, geom,
       GREATEST(no2_annuel_urbain, no2_annuel_rural) AS no2_annuel,
       GREATEST(no2_max24h_urbain, no2_max24h_rural) AS no2_max24h,
       GREATEST(no2_max1h_urbain,  no2_max1h_rural)  AS no2_max1h
FROM sensibles;

-- 1. Synthèse par type d'établissement : fourchette rural–urbain et quotient de danger de l'enveloppe
SELECT type, count(*) AS n,
       round(max(no2_annuel_rural)::numeric, 3) || ' – ' || round(max(no2_annuel_urbain)::numeric, 3) AS annuel_rural_urbain,
       round(max(no2_max24h_rural)::numeric, 2) || ' – ' || round(max(no2_max24h_urbain)::numeric, 2) AS max24h_rural_urbain,
       round(max(no2_max1h_rural)::numeric, 1)  || ' – ' || round(max(no2_max1h_urbain)::numeric, 1)  AS max1h_rural_urbain,
       round((max(GREATEST(no2_annuel_urbain, no2_annuel_rural)) / 10)::numeric, 3)  AS qd_annuel_oms,
       round((max(GREATEST(no2_max1h_urbain, no2_max1h_rural)) / 200)::numeric, 3)   AS qd_1h_oms
FROM sensibles GROUP BY type ORDER BY max(no2_annuel_urbain) DESC;

-- 2. Les cinq établissements les plus exposés, avec l'exposition totale (fond + usine)
WITH fond AS (
    SELECT avg(valeur) AS no2_fond FROM mesures WHERE station = 'FR14012' AND polluant = 'no2'
)
SELECT s.type, s.nom, round(s.distance_m) AS distance_m,
       round(s.no2_annuel::numeric, 3)                         AS no2_usine,
       round(f.no2_fond::numeric, 1)                           AS no2_fond,
       round((f.no2_fond + s.no2_annuel)::numeric, 1)          AS no2_total,
       round((100 * s.no2_annuel / (f.no2_fond + s.no2_annuel))::numeric, 2) AS part_usine_pct,
       round((s.no2_annuel / 10)::numeric, 3)                  AS qd_usine,
       round(((f.no2_fond + s.no2_annuel) / 10)::numeric, 2)   AS qd_total
FROM sensibles_enveloppe s CROSS JOIN fond f
ORDER BY s.no2_annuel DESC LIMIT 5;
