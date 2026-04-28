import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import text

root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from pipeline.db import get_engine
from pipeline.silver.iris_utils import charger_iris


TRANSPORT_WEIGHTS = {
    "norm_arrets_bus": 0.30,
    "norm_gares_metro": 0.35,
    "norm_gares_rer": 0.15,
    "norm_gares_tramway": 0.12,
    "norm_gares_train": 0.05,
}

W_TRANSPORT = 0.75
W_VELIB = 0.25


def _normalize(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce").fillna(0)
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.0, index=series.index)
    return (series - mn) / (mx - mn)


def charger_iris_ref() -> pd.DataFrame:
    gdf = charger_iris()
    df = gdf[["code_iris", "insee_com"]].copy()
    df["code_iris"] = df["code_iris"].astype(str)
    df["arrondissement"] = df["insee_com"].astype(str).str[-2:].astype(int)
    return df[["code_iris", "arrondissement"]].drop_duplicates("code_iris")


def agreger_mobilite(engine):
    arrets = pd.read_sql(
        """
        SELECT code_iris::text AS code_iris, COUNT(*) AS nb_arrets_bus
        FROM silver.map_arrets
        WHERE code_iris IS NOT NULL AND type = 'bus'
        GROUP BY code_iris
        """,
        engine,
    )

    gares = pd.read_sql(
        """
        SELECT
            code_iris::text AS code_iris,
            COUNT(*) FILTER (WHERE mode = 'METRO') AS nb_gares_metro,
            COUNT(*) FILTER (WHERE mode = 'RER') AS nb_gares_rer,
            COUNT(*) FILTER (WHERE mode = 'TRAIN') AS nb_gares_train,
            COUNT(*) FILTER (WHERE mode = 'TRAMWAY') AS nb_gares_tramway
        FROM silver.map_gares
        WHERE code_iris IS NOT NULL
        GROUP BY code_iris
        """,
        engine,
    )

    velib = pd.read_sql(
        """
        SELECT
            code_iris::text AS code_iris,
            COUNT(*) AS nb_stations_velib,
            COALESCE(SUM(capacite), 0)::int AS capacite_velib
        FROM silver.map_velib
        WHERE code_iris IS NOT NULL
        GROUP BY code_iris
        """,
        engine,
    )

    return arrets, gares, velib


def calculer_indicateurs(df_iris, arrets, gares, velib):
    df = df_iris.copy()

    for agg in [arrets, gares, velib]:
        df = df.merge(agg, on="code_iris", how="left")

    count_cols = [
        "nb_arrets_bus",
        "nb_gares_metro",
        "nb_gares_rer",
        "nb_gares_train",
        "nb_gares_tramway",
        "nb_stations_velib",
        "capacite_velib",
    ]
    for col in count_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in count_cols:
        df[f"norm_{col.replace('nb_', '')}"] = _normalize(df[col])

    # Keep column names explicit and stable for SQL.
    df = df.rename(
        columns={
            "norm_arrets_bus": "norm_arrets_bus",
            "norm_gares_metro": "norm_gares_metro",
            "norm_gares_rer": "norm_gares_rer",
            "norm_gares_train": "norm_gares_train",
            "norm_gares_tramway": "norm_gares_tramway",
            "norm_stations_velib": "norm_stations_velib",
            "norm_capacite_velib": "norm_capacite_velib",
        }
    )

    df["score_transport_collectif_raw"] = 0.0
    for col, weight in TRANSPORT_WEIGHTS.items():
        df["score_transport_collectif_raw"] += weight * df[col]

    df["score_velib_raw"] = (
        0.40 * df["norm_stations_velib"] + 0.60 * df["norm_capacite_velib"]
    )

    df["score_transport_collectif"] = _normalize(df["score_transport_collectif_raw"])
    df["score_velib"] = _normalize(df["score_velib_raw"])

    df["score_mobilite_raw"] = (
        W_TRANSPORT * df["score_transport_collectif"] + W_VELIB * df["score_velib"]
    )
    df["score_mobilite"] = _normalize(df["score_mobilite_raw"])

    score_cols = [
        "score_transport_collectif",
        "score_velib",
        "score_mobilite",
        "norm_arrets_bus",
        "norm_gares_metro",
        "norm_gares_rer",
        "norm_gares_train",
        "norm_gares_tramway",
        "norm_stations_velib",
        "norm_capacite_velib",
    ]
    for col in score_cols:
        df[col] = df[col].round(4)

    df["rang_mobilite"] = (
        df["score_mobilite"].rank(ascending=False, method="min").astype(int)
    )
    df["created_at"] = datetime.now()

    return df[
        [
            "code_iris",
            "arrondissement",
            "nb_arrets_bus",
            "nb_gares_metro",
            "nb_gares_rer",
            "nb_gares_train",
            "nb_gares_tramway",
            "nb_stations_velib",
            "capacite_velib",
            "norm_arrets_bus",
            "norm_gares_metro",
            "norm_gares_rer",
            "norm_gares_train",
            "norm_gares_tramway",
            "norm_stations_velib",
            "norm_capacite_velib",
            "score_transport_collectif",
            "score_velib",
            "score_mobilite",
            "rang_mobilite",
            "created_at",
        ]
    ]


def upsert_gold(engine, df):
    upsert_sql = text(
        """
        INSERT INTO gold.indicateurs_mobilite_iris (
            code_iris, arrondissement,
            nb_arrets_bus, nb_gares_metro, nb_gares_rer, nb_gares_train,
            nb_gares_tramway, nb_stations_velib, capacite_velib,
            norm_arrets_bus, norm_gares_metro, norm_gares_rer, norm_gares_train,
            norm_gares_tramway, norm_stations_velib,
            norm_capacite_velib,
            score_transport_collectif, score_velib, score_mobilite,
            rang_mobilite, created_at
        ) VALUES (
            :code_iris, :arrondissement,
            :nb_arrets_bus, :nb_gares_metro, :nb_gares_rer, :nb_gares_train,
            :nb_gares_tramway, :nb_stations_velib, :capacite_velib,
            :norm_arrets_bus, :norm_gares_metro, :norm_gares_rer,
            :norm_gares_train, :norm_gares_tramway,
            :norm_stations_velib, :norm_capacite_velib,
            :score_transport_collectif, :score_velib, :score_mobilite,
            :rang_mobilite, :created_at
        )
        ON CONFLICT (code_iris) DO UPDATE SET
            arrondissement = EXCLUDED.arrondissement,
            nb_arrets_bus = EXCLUDED.nb_arrets_bus,
            nb_gares_metro = EXCLUDED.nb_gares_metro,
            nb_gares_rer = EXCLUDED.nb_gares_rer,
            nb_gares_train = EXCLUDED.nb_gares_train,
            nb_gares_tramway = EXCLUDED.nb_gares_tramway,
            nb_stations_velib = EXCLUDED.nb_stations_velib,
            capacite_velib = EXCLUDED.capacite_velib,
            norm_arrets_bus = EXCLUDED.norm_arrets_bus,
            norm_gares_metro = EXCLUDED.norm_gares_metro,
            norm_gares_rer = EXCLUDED.norm_gares_rer,
            norm_gares_train = EXCLUDED.norm_gares_train,
            norm_gares_tramway = EXCLUDED.norm_gares_tramway,
            norm_stations_velib = EXCLUDED.norm_stations_velib,
            norm_capacite_velib = EXCLUDED.norm_capacite_velib,
            score_transport_collectif = EXCLUDED.score_transport_collectif,
            score_velib = EXCLUDED.score_velib,
            score_mobilite = EXCLUDED.score_mobilite,
            rang_mobilite = EXCLUDED.rang_mobilite,
            created_at = EXCLUDED.created_at
        """
    )

    with engine.begin() as conn:
        conn.execute(upsert_sql, df.to_dict(orient="records"))

    print(f"gold.indicateurs_mobilite_iris : {len(df)} lignes upsertées")


def run(engine):
    print("[gold.mobilite] Chargement du référentiel IRIS...")
    df_iris = charger_iris_ref()
    print(f"  {len(df_iris)} IRIS parisiens")

    print("[gold.mobilite] Agrégation des tables silver mobilité...")
    arrets, gares, velib = agreger_mobilite(engine)
    print(
        f"  arrets: {len(arrets)} IRIS, gares: {len(gares)} IRIS, "
        f"velib: {len(velib)} IRIS"
    )

    print("[gold.mobilite] Normalisation et calcul des scores...")
    result = calculer_indicateurs(df_iris, arrets, gares, velib)
    print(
        f"  score min={result['score_mobilite'].min():.4f}, "
        f"max={result['score_mobilite'].max():.4f}, "
        f"moyen={result['score_mobilite'].mean():.4f}"
    )

    upsert_gold(engine, result)


def main():
    engine = get_engine()
    run(engine)


if __name__ == "__main__":
    main()
