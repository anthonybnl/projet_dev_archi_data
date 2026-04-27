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

CREATE TABLE IF NOT EXISTS gold.indicateurs_logements_sociaux_iris (
    code_iris                       TEXT,
    annee                           INTEGER,
    arrondissement                  INTEGER,
    nb_logements_sociaux_finances   INTEGER,
    nb_plai                         INTEGER,
    nb_plus                         INTEGER,
    nb_plus_cd                      INTEGER,
    nb_pls                          INTEGER,
    PRIMARY KEY (code_iris, annee)
);

CREATE TABLE IF NOT EXISTS gold.indicateurs_socio_eco_iris (
    code_iris               TEXT,
    annee                   INTEGER,
    arrondissement          INTEGER,
    revenu_median           DOUBLE PRECISION,
    prix_m2_median          DOUBLE PRECISION,
    iai                     DOUBLE PRECISION,
    PRIMARY KEY (code_iris, annee)
);
