import sys
from pathlib import Path
import json
from datetime import datetime

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

root_path = Path(__file__).resolve().parents[2]

if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from pipeline.config import PATHS
from pipeline.db import insert_if_empty, get_engine

# Poids du score final, validés en réunion projet
W_MOBILE = 0.45
W_QUALITE = 0.35
W_FIBRE = 0.20


def load_iris_gdf() -> gpd.GeoDataFrame:
    with open(PATHS["iris_geojson"], encoding="utf-8") as f:
        geojson = json.load(f)
    rows = []
    for feat in geojson["features"]:
        props = feat["properties"]
        if props.get("dep") != "75":
            continue
        rows.append(
            {"code_iris": props["code_iris"], "geometry": shape(feat["geometry"])}
        )
    return gpd.GeoDataFrame(rows, crs="EPSG:4326").to_crs("EPSG:2154")


def interpolate_qualite(
    qualite_iris: pd.DataFrame, iris_gdf: gpd.GeoDataFrame
) -> pd.DataFrame:
    """
    Pour les IRIS sans mesure QoS, on interpole le score_qualite
    depuis les IRIS voisins (ceux qui partagent une frontière).
    On répète jusqu'à 3 passes pour couvrir les IRIS isolés.
    """
    scores = iris_gdf[["code_iris"]].merge(qualite_iris, on="code_iris", how="left")
    scores["score_qualite"] = pd.to_numeric(scores["score_qualite"], errors="coerce")

    # Construction du graphe de voisinage : deux IRIS voisins = géométries qui se touchent
    iris_geo = iris_gdf.set_index("code_iris")

    for _ in range(3):
        manquants = scores[scores["score_qualite"].isna()]["code_iris"].tolist()
        if not manquants:
            break

        for code in manquants:
            geom = iris_geo.loc[code, "geometry"]
            # IRIS voisins = ceux dont la géométrie touche ou intersecte la frontière
            voisins_mask = iris_geo.geometry.touches(
                geom
            ) | iris_geo.geometry.intersects(geom.boundary)
            voisins_codes = iris_geo[voisins_mask].index.tolist()
            voisins_codes = [c for c in voisins_codes if c != code]

            valeurs_voisins = scores.loc[
                scores["code_iris"].isin(voisins_codes)
                & scores["score_qualite"].notna(),
                "score_qualite",
            ]
            if len(valeurs_voisins) > 0:
                scores.loc[scores["code_iris"] == code, "score_qualite"] = (
                    valeurs_voisins.mean().round(2)
                )

    # Les IRIS encore sans valeur après interpolation reçoivent la médiane globale
    mediane = scores["score_qualite"].median()
    scores["score_qualite"] = scores["score_qualite"].fillna(mediane).round(2)

    return scores[["code_iris", "score_qualite"]]


def run(engine):
    silver = "silver"
    gold = "gold"

    print("[gold.score_reseau] Lecture des tables silver reseau...")
    mobile = pd.read_sql(f"SELECT * FROM {silver}.reseau_mobile", engine)
    qualite = pd.read_sql(f"SELECT * FROM {silver}.reseau_qualite", engine)
    fibre = pd.read_sql(f"SELECT * FROM {silver}.reseau_fibre", engine)

    # --- Score mobile par IRIS ---
    # Max par opérateur : un habitant choisit son forfait,
    # il bénéficie du meilleur opérateur disponible dans sa zone.
    mobile_iris = (
        mobile.groupby(["code_iris", "arrondissement"])
        .agg(
            couv_4g_max=("couv_4g", "max"),
            couv_5g_max=("couv_5g", "max"),
            score_mobile=("score_mobile", "max"),
        )
        .reset_index()
    )

    # Meilleur opérateur mobile = celui avec le score_mobile le plus élevé par IRIS
    idx_mobile = mobile.groupby("code_iris")["score_mobile"].idxmax()
    best_mobile = mobile.loc[idx_mobile, ["code_iris", "operateur"]].rename(
        columns={"operateur": "meilleur_operateur_mobile"}
    )

    # --- Score qualité par IRIS avec interpolation spatiale ---
    print(
        "[gold.score_reseau] Interpolation spatiale QoS pour les IRIS sans mesures..."
    )
    iris_gdf = load_iris_gdf()

    if len(qualite) > 0:
        qualite_iris = (
            qualite.groupby("code_iris")
            .agg(
                score_qualite=("score_qualite", "max"),
            )
            .reset_index()
        )
        # Interpolation : IRIS sans mesures ← moyenne des voisins avec mesures
        qualite_iris = interpolate_qualite(qualite_iris, iris_gdf)
    else:
        qualite_iris = iris_gdf[["code_iris"]].assign(score_qualite=0.0)

    # --- Assemblage ---
    result = mobile_iris.merge(qualite_iris, on="code_iris", how="left")

    result = result.merge(
        fibre[
            [
                "code_iris",
                "taux_deploiement",
                "taux_pm_actif",
                "score_fibre",
                "meilleur_operateur_fibre",
            ]
        ],
        on="code_iris",
        how="left",
    )
    result = result.merge(best_mobile, on="code_iris", how="left")

    # Certains IRIS peuvent manquer de mesures QoS ou fibre, on pénalise sans supprimer
    for col in ["score_mobile", "score_qualite", "score_fibre"]:
        result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0)

    result["score_final"] = (
        W_MOBILE * result["score_mobile"]
        + W_QUALITE * result["score_qualite"]
        + W_FIBRE * result["score_fibre"]
    ).round(2)

    result["rang_reseau"] = (
        result["score_final"].rank(ascending=False, method="min").astype(int)
    )

    result = result.rename(columns={"taux_deploiement": "taux_deploiement_fibre"})

    result["created_at"] = datetime.now()

    cols = [
        "code_iris",
        "arrondissement",
        "rang_reseau",
        "score_final",
        "score_mobile",
        "score_qualite",
        "score_fibre",
        "couv_4g_max",
        "couv_5g_max",
        "taux_deploiement_fibre",
        "taux_pm_actif",
        "meilleur_operateur_mobile",
        "meilleur_operateur_fibre",
        "created_at",
    ]
    result = result[cols].sort_values("rang_reseau")

    inserted = insert_if_empty(result, "score_reseau", engine, gold)
    if inserted:
        print(f"[gold.score_reseau] {len(result)} IRIS inseres")
        print(
            result[
                [
                    "code_iris",
                    "arrondissement",
                    "rang_reseau",
                    "score_final",
                    "meilleur_operateur_mobile",
                    "meilleur_operateur_fibre",
                ]
            ]
            .head(10)
            .to_string(index=False)
        )
    else:
        print("[gold.score_reseau] table deja remplie, aucune insertion")


def main():
    engine = get_engine()
    run(engine)


if __name__ == "__main__":
    main()
