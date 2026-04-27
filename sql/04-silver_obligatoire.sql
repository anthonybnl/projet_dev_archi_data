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

CREATE TABLE IF NOT EXISTS silver.filosofi (
    code_iris               TEXT,
    annee                   INTEGER,
    revenu_median           DOUBLE PRECISION,
    arrondissement          INTEGER,
    PRIMARY KEY (code_iris, annee)
);

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
