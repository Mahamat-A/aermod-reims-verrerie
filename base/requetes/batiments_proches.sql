-- Bâtiments de plus de 15 m à moins de 300 m de la cheminée A, avec la hauteur BPE (règle simplifiée)
-- H_BPE = H + 1,5 × min(H, largeur) ; largeur approchée par la racine de l'emprise
WITH cheminee AS (
    SELECT ST_SetSRID(ST_MakePoint(576601.2, 5453845.2), 32631) AS geom, 59.0 AS hauteur
)
SELECT b.usage,
       b.hauteur                                                        AS h_m,
       round(ST_Distance(b.geom, c.geom))                               AS distance_m,
       round(ST_Area(b.geom))                                           AS emprise_m2,
       round((b.hauteur + 1.5 * least(b.hauteur, sqrt(ST_Area(b.geom))))::numeric, 1) AS h_bpe_m,
       CASE WHEN b.hauteur + 1.5 * least(b.hauteur, sqrt(ST_Area(b.geom))) > c.hauteur
            THEN 'rabattement possible' ELSE '' END                     AS verdict
FROM batiments b, cheminee c
WHERE b.hauteur > 15
  AND ST_DWithin(b.geom, c.geom, 300)
ORDER BY h_bpe_m DESC;
