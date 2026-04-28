CREATE TABLE IF NOT EXISTS silver.map_arrets (
    arret_id        INTEGER         PRIMARY KEY,
    nom             VARCHAR(255)    NOT NULL,
    type            VARCHAR(50),
    lat             DOUBLE PRECISION,
    lon             DOUBLE PRECISION,
    code_iris       INTEGER,
    nom_iris        VARCHAR(255),
    arrondissement  INTEGER,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.map_gares (
    gare_id         INTEGER         PRIMARY KEY,
    nom             VARCHAR(255)    NOT NULL,
    mode            VARCHAR(50),
    ligne           VARCHAR(100),
    exploitant      VARCHAR(100),
    lat             DOUBLE PRECISION,
    lon             DOUBLE PRECISION,
    code_iris       INTEGER,
    nom_iris        VARCHAR(255),
    arrondissement  INTEGER,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

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
