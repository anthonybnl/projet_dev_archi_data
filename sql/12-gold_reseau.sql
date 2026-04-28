-- Une ligne par code_iris — table de sortie finale du pipeline réseau.
-- Agrège les trois sous-scores silver en un score réseau unique exposé au front.
DROP TABLE IF EXISTS gold.score_reseau;
CREATE TABLE gold.score_reseau (
    id                        SERIAL       PRIMARY KEY,
    code_iris                 VARCHAR(9)   NOT NULL UNIQUE,
    arrondissement            SMALLINT     NOT NULL,
    rang_reseau               SMALLINT     NOT NULL,
    score_final               NUMERIC(5,2) NOT NULL,
    score_mobile              NUMERIC(5,2),
    score_qualite             NUMERIC(5,2),
    score_fibre               NUMERIC(5,2),
    couv_4g_max               NUMERIC(5,2),
    couv_5g_max               NUMERIC(5,2),
    taux_deploiement_fibre    NUMERIC(5,2),
    taux_pm_actif             NUMERIC(5,2),
    meilleur_operateur_mobile VARCHAR(20),
    meilleur_operateur_fibre  VARCHAR(20),
    created_at                TIMESTAMP    NOT NULL DEFAULT NOW()
);
