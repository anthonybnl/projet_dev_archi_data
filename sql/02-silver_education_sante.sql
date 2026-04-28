CREATE TABLE IF NOT EXISTS silver.colleges_paris (
    id              VARCHAR(300)    PRIMARY KEY,   -- adresse + arrondissement (ex: "101 AVENUE DE LA REPUBLIQUE 11e")
    nom             VARCHAR(255)    NOT NULL,
    adresse         VARCHAR(255),
    arrondissement  SMALLINT        NOT NULL,
    lat             DOUBLE PRECISION,
    lon             DOUBLE PRECISION,
    code_iris       INTEGER,
    nom_iris        VARCHAR(255),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

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
    code_iris           INTEGER,
    nom_iris            VARCHAR(255),
    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_map_sante_finess UNIQUE (finess)
);

CREATE TABLE IF NOT EXISTS silver.map_scolaire (
    id              VARCHAR(300)    PRIMARY KEY,   -- adresse + arrondissement (ex: "7 RUE DOUDEAUVILLE 18e")
    nom             VARCHAR(255)    NOT NULL,
    adresse         VARCHAR(255),
    type            VARCHAR(50)     NOT NULL,      -- Élémentaire, Maternelle, Polyvalent, Collège
    arrondissement  SMALLINT        NOT NULL,
    lat             DOUBLE PRECISION,
    lon             DOUBLE PRECISION,
    code_iris       INTEGER,
    nom_iris        VARCHAR(255),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.population_enfants_paris (
    id              SERIAL      PRIMARY KEY,
    arrondissement  SMALLINT    NOT NULL,
    pop_3_10        INTEGER     NOT NULL,
    pop_11_17       INTEGER     NOT NULL,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.population_totale_paris (
    id                  SERIAL      PRIMARY KEY,
    arrondissement      SMALLINT    NOT NULL,
    population_totale   INTEGER     NOT NULL,
    created_at          TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.population_iris (
    code_iris       TEXT            PRIMARY KEY,
    arrondissement  SMALLINT        NOT NULL,
    pop_totale      DOUBLE PRECISION NOT NULL,
    pop_3_10        DOUBLE PRECISION NOT NULL,
    pop_11_17       DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS silver.sante_paris (
    id                  SERIAL      PRIMARY KEY,
    arrondissement      SMALLINT    NOT NULL,
    nb_medecins         INTEGER     NOT NULL DEFAULT 0,
    nb_infirmiers       INTEGER     NOT NULL DEFAULT 0,
    nb_centres_sante    INTEGER     NOT NULL DEFAULT 0,
    nb_pharmacies       INTEGER     NOT NULL DEFAULT 0,
    created_at          TIMESTAMP   NOT NULL DEFAULT NOW()
);
