CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.dvf (
    id_mutation             TEXT PRIMARY KEY,
    date_mutation           DATE,
    nature_mutation         TEXT,
    valeur_fonciere         DOUBLE PRECISION,
    no_voie                 TEXT,
    type_voie               TEXT,
    voie                    TEXT,
    code_postal             TEXT,
    commune                 TEXT,
    code_departement        TEXT,
    code_commune            TEXT,
    arrondissement          INTEGER,
    section                 TEXT,
    no_plan                 TEXT,
    type_local              TEXT,
    surface_reelle_bati     INTEGER,
    nombre_pieces           INTEGER,
    surface_terrain         INTEGER,
    latitude                DOUBLE PRECISION,
    longitude               DOUBLE PRECISION,
    code_iris               TEXT
);
