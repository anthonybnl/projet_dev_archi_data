-- Une ligne par (code_iris, opérateur).
-- Métriques de qualité mesurée : débit réel, latence, fiabilité (sources QoS ARCEP + Ookla).
DROP TABLE IF EXISTS silver.reseau_qualite;
CREATE TABLE silver.reseau_qualite (
    id              SERIAL      PRIMARY KEY,
    code_iris       VARCHAR(9)  NOT NULL,
    arrondissement  SMALLINT    NOT NULL,
    operateur       VARCHAR(20) NOT NULL,
    score_debit     NUMERIC(5,2),
    score_fiabilite NUMERIC(5,2),
    score_latence   NUMERIC(5,2),
    score_qualite   NUMERIC(5,2),
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);
