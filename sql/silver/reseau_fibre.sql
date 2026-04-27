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
