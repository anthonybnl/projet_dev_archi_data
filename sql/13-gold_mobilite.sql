CREATE TABLE gold.indicateurs_mobilite_iris (
    code_iris                   VARCHAR(9)   PRIMARY KEY,
    arrondissement              SMALLINT     NOT NULL,

    nb_arrets_bus               INTEGER      NOT NULL DEFAULT 0,
    nb_gares_metro              INTEGER      NOT NULL DEFAULT 0,
    nb_gares_rer                INTEGER      NOT NULL DEFAULT 0,
    nb_gares_train              INTEGER      NOT NULL DEFAULT 0,
    nb_gares_tramway            INTEGER      NOT NULL DEFAULT 0,
    nb_stations_velib           INTEGER      NOT NULL DEFAULT 0,
    capacite_velib              INTEGER      NOT NULL DEFAULT 0,

    norm_arrets_bus             DOUBLE PRECISION NOT NULL,
    norm_gares_metro            DOUBLE PRECISION NOT NULL,
    norm_gares_rer              DOUBLE PRECISION NOT NULL,
    norm_gares_train            DOUBLE PRECISION NOT NULL,
    norm_gares_tramway          DOUBLE PRECISION NOT NULL,
    norm_stations_velib         DOUBLE PRECISION NOT NULL,
    norm_capacite_velib         DOUBLE PRECISION NOT NULL,

    score_transport_collectif   DOUBLE PRECISION NOT NULL,
    score_velib                 DOUBLE PRECISION NOT NULL,
    score_mobilite              DOUBLE PRECISION NOT NULL,
    rang_mobilite               INTEGER      NOT NULL,
    created_at                  TIMESTAMP    NOT NULL DEFAULT NOW()
);
