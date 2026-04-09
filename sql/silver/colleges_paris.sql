CREATE TABLE IF NOT EXISTS silver.colleges_paris (
    id              VARCHAR(300)    PRIMARY KEY,   -- adresse + arrondissement (ex: "101 AVENUE DE LA REPUBLIQUE 11e")
    nom             VARCHAR(255)    NOT NULL,
    adresse         VARCHAR(255),
    arrondissement  SMALLINT        NOT NULL,
    lat             DOUBLE PRECISION,
    lon             DOUBLE PRECISION,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);
