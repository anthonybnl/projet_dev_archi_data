import sys
from pathlib import Path

import pandas as pd
import geopandas as gpd
from sqlalchemy import text

root_path = Path(__file__).resolve().parents[2]

if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from pipeline.db import get_engine

DATA_DIR = root_path / "data" / "raw"

POIDS = {
    "arbres": 0.30,
    "espaces_verts": 0.40,
    "ilots_fraicheur": 0.20,
    "trilib": 0.10,
}


def charger_iris_ref():
    gdf = gpd.read_file(DATA_DIR / "map" / "iris.geojson")
    gdf = gdf[gdf["insee_com"].astype(str).str.startswith("751")]

    df = pd.DataFrame(
        {
            "code_iris": gdf["code_iris"].values,
        }
    )

    df["arrondissement"] = df["code_iris"].str[:5].str[-2:].astype(int)

    return df


def agreger(engine):
    nb_arbres = pd.read_sql(
        """
        SELECT code_iris, COUNT(*) AS nb_arbres
        FROM silver.arbres
        WHERE code_iris IS NOT NULL
        GROUP BY code_iris
    """,
        engine,
    )

    superficie_ev = pd.read_sql(
        """
        SELECT code_iris, SUM(superficie) AS superficie_ev
        FROM silver.espaces_verts
        WHERE code_iris IS NOT NULL
        GROUP BY code_iris
    """,
        engine,
    )

    nb_ilots = pd.read_sql(
        """
        SELECT code_iris, COUNT(DISTINCT id) AS nb_ilots
        FROM silver.ilots_fraicheur
        WHERE code_iris IS NOT NULL
        GROUP BY code_iris
    """,
        engine,
    )

    nb_trilib = pd.read_sql(
        """
        SELECT code_iris, COUNT(*) AS nb_trilib
        FROM silver.trilib
        WHERE code_iris IS NOT NULL
        GROUP BY code_iris
    """,
        engine,
    )

    return nb_arbres, superficie_ev, nb_ilots, nb_trilib


def normaliser_et_scorer(
    df_iris: pd.DataFrame, nb_arbres, superficie_ev, nb_ilots, nb_trilib
):
    df = df_iris.copy()

    for agg, col in [
        (nb_arbres, "nb_arbres"),
        (superficie_ev, "superficie_ev"),
        (nb_ilots, "nb_ilots"),
        (nb_trilib, "nb_trilib"),
    ]:
        df = df.merge(agg, on="code_iris", how="left")
        df[col] = df[col].fillna(0)

    df["rang_arbres"] = df["nb_arbres"].rank(method="average", pct=True)
    df["rang_ev"] = df["superficie_ev"].rank(method="average", pct=True)
    df["rang_ilots"] = df["nb_ilots"].rank(method="average", pct=True)
    df["rang_trilib"] = df["nb_trilib"].rank(method="average", pct=True)

    df["score"] = (
        POIDS["arbres"] * df["rang_arbres"]
        + POIDS["espaces_verts"] * df["rang_ev"]
        + POIDS["ilots_fraicheur"] * df["rang_ilots"]
        + POIDS["trilib"] * df["rang_trilib"]
    ).round(4)

    return df[["code_iris", "arrondissement", "score"]]


def upsert_gold(engine, gold):
    upsert_sql = text(
        """
        INSERT INTO gold.score_environnemental (code_iris, arrondissement, score)
        VALUES (:code_iris, :arrondissement, :score)
        ON CONFLICT (code_iris) DO UPDATE SET
            arrondissement = EXCLUDED.arrondissement,
            score = EXCLUDED.score
    """
    )

    with engine.begin() as conn:
        for _, row in gold.iterrows():
            conn.execute(
                upsert_sql,
                {
                    "code_iris": row["code_iris"],
                    "arrondissement": int(row["arrondissement"]),
                    "score": float(row["score"]),
                },
            )

    print(f"gold.score_environnemental : {len(gold)} lignes upsertées")


def main():
    engine = get_engine()

    print("Chargement du référentiel IRIS...")
    df_iris = charger_iris_ref()
    print(f"  {len(df_iris)} IRIS parisiens")

    print("Agrégation des indicateurs silver...")
    nb_arbres, superficie_ev, nb_ilots, nb_trilib = agreger(engine)
    print(
        f"  arbres: {len(nb_arbres)} IRIS, espaces_verts: {len(superficie_ev)} IRIS, "
        f"ilots: {len(nb_ilots)} IRIS, trilib: {len(nb_trilib)} IRIS"
    )

    print("Normalisation et calcul du score...")
    gold = normaliser_et_scorer(df_iris, nb_arbres, superficie_ev, nb_ilots, nb_trilib)
    print(
        f"  score min={gold['score'].min():.4f}, max={gold['score'].max():.4f}, "
        f"median={gold['score'].median():.4f}"
    )

    print("Insertion dans gold...")
    upsert_gold(engine, gold)


if __name__ == "__main__":
    main()
