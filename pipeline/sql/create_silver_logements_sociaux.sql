CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.logements_sociaux (
    identifiant_livraison   TEXT PRIMARY KEY,
    adresse                 TEXT,
    code_postal             TEXT,
    ville                   TEXT,
    annee_financement       INTEGER,
    bailleur_social         TEXT,
    nb_logements_finances   INTEGER,
    nb_plai                 INTEGER,
    nb_plus                 INTEGER,
    nb_plus_cd              INTEGER,
    nb_pls                  INTEGER,
    mode_realisation        TEXT,
    commentaires            TEXT,
    arrondissement          INTEGER,
    nature_programme        TEXT,
    x_l93                   DOUBLE PRECISION,
    y_l93                   DOUBLE PRECISION,
    latitude                DOUBLE PRECISION,
    longitude               DOUBLE PRECISION,
    code_iris               TEXT
);
