CREATE TABLE IF NOT EXISTS silver.elementaires_maternelles_effectifs (
    id                      SERIAL          PRIMARY KEY,
    numero_ecole            VARCHAR(20)     NOT NULL,
    nom                     VARCHAR(255),
    type                    VARCHAR(100),
    secteur                 VARCHAR(50),
    arrondissement          SMALLINT        NOT NULL,
    nb_eleves               INTEGER         NOT NULL,
    created_at              TIMESTAMP       NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_ecoles_numero UNIQUE (numero_ecole)
);
