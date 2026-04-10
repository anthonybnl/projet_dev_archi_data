CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.indicateurs_dvf_iris (
    code_iris               TEXT,
    annee                   INTEGER,
    arrondissement          INTEGER,
    nb_transactions         INTEGER,
    prix_m2_median          DOUBLE PRECISION,
    prix_m2_moyen           DOUBLE PRECISION,
    nb_appartements         INTEGER,
    nb_maisons              INTEGER,
    PRIMARY KEY (code_iris, annee)
);
