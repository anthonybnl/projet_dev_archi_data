CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.indicateurs_socio_eco_iris (
    code_iris               TEXT,
    annee                   INTEGER,
    arrondissement          INTEGER,
    revenu_median           DOUBLE PRECISION,
    prix_m2_median          DOUBLE PRECISION,
    iai                     DOUBLE PRECISION,
    PRIMARY KEY (code_iris, annee)
);
