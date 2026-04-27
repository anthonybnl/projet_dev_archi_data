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
