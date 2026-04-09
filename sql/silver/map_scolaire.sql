CREATE TABLE IF NOT EXISTS silver.map_scolaire (
    id              VARCHAR(300)    PRIMARY KEY,   -- adresse + arrondissement (ex: "7 RUE DOUDEAUVILLE 18e")
    nom             VARCHAR(255)    NOT NULL,
    adresse         VARCHAR(255),
    type            VARCHAR(50)     NOT NULL,      -- Élémentaire, Maternelle, Polyvalent, Collège
    arrondissement  SMALLINT        NOT NULL,
    lat             DOUBLE PRECISION,
    lon             DOUBLE PRECISION,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);
