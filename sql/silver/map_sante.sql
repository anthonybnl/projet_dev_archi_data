CREATE TABLE IF NOT EXISTS silver.map_sante (
    id                  SERIAL          PRIMARY KEY,
    finess              VARCHAR(20)     NOT NULL,
    nom                 VARCHAR(255)    NOT NULL,
    adresse             VARCHAR(255),
    telephone           VARCHAR(20),
    categorie           VARCHAR(150),
    type_etablissement  VARCHAR(150),
    cp_ville            VARCHAR(50),
    arrondissement      SMALLINT        NOT NULL,
    lat                 DOUBLE PRECISION,
    lon                 DOUBLE PRECISION,
    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_map_sante_finess UNIQUE (finess)
);
