CREATE TABLE "silver"."arbres" (
    id INT PRIMARY KEY,
    arrondissement INT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    code_iris TEXT
);

CREATE TABLE "silver"."espaces_verts" (
    id            INT,
    nom           TEXT,
    code_postal   INT,
    superficie    DOUBLE PRECISION,
    annee         INT,
    code_iris     TEXT,
    PRIMARY KEY (id, code_iris)
);
