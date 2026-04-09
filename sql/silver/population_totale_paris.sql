CREATE TABLE IF NOT EXISTS silver.population_totale_paris (
    id                  SERIAL      PRIMARY KEY,
    arrondissement      SMALLINT    NOT NULL,
    population_totale   INTEGER     NOT NULL,
    created_at          TIMESTAMP   NOT NULL DEFAULT NOW()
);
