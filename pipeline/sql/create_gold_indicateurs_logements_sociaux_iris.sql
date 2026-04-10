CREATE SCHEMA IF NOT EXISTS gold;

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
