CREATE TABLE IF NOT EXISTS silver.map_velib (
    station_id      VARCHAR(20)     PRIMARY KEY,
    nom             VARCHAR(255)    NOT NULL,
    capacite        INTEGER,
    lat             DOUBLE PRECISION,
    lon             DOUBLE PRECISION,
    code_iris       INTEGER,
    nom_iris        VARCHAR(255),
    arrondissement  INTEGER,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);
