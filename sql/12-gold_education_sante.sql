CREATE TABLE IF NOT EXISTS gold.indicateurs_aes_arrondissement (
    arrondissement          SMALLINT    PRIMARY KEY,

    -- Education (bruts)
    e1_scolarisation        DOUBLE PRECISION,  -- nb_eleves_primaire / pop_3_10
    e2_couverture_college   DOUBLE PRECISION,  -- nb_colleges / pop_11_17

    -- Sante (bruts, ratio pour 10 000 hab)
    s1_medecins                 DOUBLE PRECISION,
    s2_infirmiers               DOUBLE PRECISION,
    s3_centres_hospitaliers     DOUBLE PRECISION,
    s4_pharmacies               DOUBLE PRECISION,

    -- Scores normalises [0, 1]
    score_education         DOUBLE PRECISION,
    score_sante             DOUBLE PRECISION,
    score_aes               DOUBLE PRECISION
);
