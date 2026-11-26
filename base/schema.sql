-- Base oi_reims : tables du projet de dispersion (verrerie O-I, Reims, 2024)
-- Toutes les heures sont en UTC, début d'heure.

CREATE TABLE IF NOT EXISTS mesures (
    station    text REFERENCES stations(code),   -- doit exister dans la table stations
    polluant   text,                             -- no, no2, nox, o3
    debut_utc  timestamp,
    valeur     real,                             -- µg/m³
    PRIMARY KEY (station, polluant, debut_utc)
);

CREATE TABLE IF NOT EXISTS meteo (
    debut_utc      timestamp PRIMARY KEY,
    vitesse        real,      -- m/s, Reims-Prunay (AERMET)
    direction      real,      -- ° d'où vient le vent
    monin_obukhov  real,      -- m (< 0 instable, > 0 stable)
    zi_conv        real,      -- hauteur de mélange convective (m)
    zi_meca        real       -- hauteur de mélange mécanique (m)
);

CREATE TABLE IF NOT EXISTS modele (
    cas        text,          -- rural ou urbain
    station    text REFERENCES stations(code),
    debut_utc  timestamp,
    nox        real,          -- contribution AERMOD de la verrerie (µg/m³)
    PRIMARY KEY (cas, station, debut_utc)
);

-- Bâtiments BD TOPO (IGN) autour de la cheminée : polygones PostGIS en UTM 31N
CREATE TABLE IF NOT EXISTS batiments (
    cleabs        text PRIMARY KEY,               -- identifiant IGN
    nature        text,
    usage         text,
    hauteur       real,                           -- m
    altitude_sol  real,                           -- m
    geom          geometry(MultiPolygon, 32631)
);
CREATE INDEX IF NOT EXISTS batiments_geom_idx ON batiments USING GIST (geom);
