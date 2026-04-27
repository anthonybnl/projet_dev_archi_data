-- Une ligne par code_iris.
-- Taux de déploiement fibre et PM actif depuis la carte nationale ARCEP.
-- arrondissement est dérivé du code_iris.
DROP TABLE IF EXISTS silver.reseau_fibre;
CREATE TABLE silver.reseau_fibre (
    id                       SERIAL       PRIMARY KEY,
    code_iris                VARCHAR(9)   NOT NULL UNIQUE,
    arrondissement           SMALLINT     NOT NULL,
    total_imb                INTEGER      NOT NULL,
    imb_deployes             INTEGER      NOT NULL,
    pm_actifs                INTEGER      NOT NULL,
    taux_deploiement         NUMERIC(5,2) NOT NULL,
    taux_pm_actif            NUMERIC(5,2) NOT NULL,
    meilleur_operateur_fibre VARCHAR(20),
    score_fibre              NUMERIC(5,2) NOT NULL,
    created_at               TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Une ligne par (code_iris, opérateur).
-- couv_4g et couv_5g sont sur la même ligne, build_result agrège les deux technologies.
-- arrondissement est dérivé du code_iris (ex : '751010205' → 1).
DROP TABLE IF EXISTS silver.reseau_mobile;
CREATE TABLE silver.reseau_mobile (
    id                   SERIAL       PRIMARY KEY,
    code_iris            VARCHAR(9)   NOT NULL,
    arrondissement       SMALLINT     NOT NULL,
    operateur            VARCHAR(20)  NOT NULL,
    couv_4g              NUMERIC(5,2),
    couv_5g              NUMERIC(5,2),
    score_niveau         SMALLINT,
    nb_antennes          INTEGER,
    densite_antennes_km2 NUMERIC(8,3),
    score_densite        NUMERIC(5,2),
    score_mobile         NUMERIC(5,2),
    created_at           TIMESTAMP    NOT NULL DEFAULT NOW()
);

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
