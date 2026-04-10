CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.filosofi (
    code_iris               TEXT,
    annee                   INTEGER,
    revenu_median           DOUBLE PRECISION,
    arrondissement          INTEGER,
    PRIMARY KEY (code_iris, annee)
);
