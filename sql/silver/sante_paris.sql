CREATE TABLE IF NOT EXISTS silver.sante_paris (
    id                  SERIAL      PRIMARY KEY,
    arrondissement      SMALLINT    NOT NULL,
    nb_medecins         INTEGER     NOT NULL DEFAULT 0,
    nb_infirmiers       INTEGER     NOT NULL DEFAULT 0,
    nb_centres_sante    INTEGER     NOT NULL DEFAULT 0,
    nb_pharmacies       INTEGER     NOT NULL DEFAULT 0,
    created_at          TIMESTAMP   NOT NULL DEFAULT NOW()
);
