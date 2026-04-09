CREATE TABLE IF NOT EXISTS silver.population_enfants_paris (
    id              SERIAL      PRIMARY KEY,
    arrondissement  SMALLINT    NOT NULL,
    pop_3_10        INTEGER     NOT NULL,
    pop_11_17       INTEGER     NOT NULL,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);
