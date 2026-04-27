import json
import warnings
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

from pipeline.config import PATHS
from pipeline.db import insert_if_empty

warnings.filterwarnings("ignore")

OPERATEURS = {
    "BOUY": "Bouygues",
    "FREE": "Free",
    "OF":   "Orange",
    "SFR0": "SFR",
}

OPERATEURS_ANTENNES = {
    "bouygues":    "Bouygues",
    "free mobile": "Free",
    "free":        "Free",
    "orange":      "Orange",
    "sfr":         "SFR",
}

# Niveaux de couverture ARCEP et leur score associé
NIVEAU_SCORE = {"TBC": 100, "BC": 60, "CL": 30}


def load_iris() -> gpd.GeoDataFrame:
    with open(PATHS["iris_geojson"], encoding="utf-8") as f:
        geojson = json.load(f)

    rows = []
    for feat in geojson["features"]:
        props = feat["properties"]
        # On garde uniquement Paris (dep = '75')
        if props.get("dep") != "75":
            continue
        # arrondissement dérivé : code_iris '751010205' → insee_com 75101 → arrond 1
        insee_com = int(props["insee_com"])
        rows.append({
            "code_iris":     props["code_iris"],
            "arrondissement": insee_com - 75100,
            "geometry":      shape(feat["geometry"]),
        })

    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    # Reprojection en Lambert-93 pour correspondre au CRS des .gpkg ARCEP
    gdf = gdf.to_crs("EPSG:2154")
    gdf["surface_m2"] = gdf.geometry.area
    return gdf


def compute_couverture(iris_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Intersection spatiale des polygones de couverture ARCEP avec chaque IRIS.
    Utilise gpd.overlay() vectorisé - beaucoup plus rapide qu'une boucle sur 992 IRIS.
    Taux = surface couverte dans l'IRIS / surface totale de l'IRIS.
    Le niveau dominant est celui du polygone qui occupe la plus grande surface d'intersection.
    """
    records = []
    couv_dir = Path(PATHS["couverture_dir"])
    iris_surf = iris_gdf.set_index("code_iris")["surface_m2"]

    for fichier in couv_dir.glob("*.gpkg"):
        # Convention de nommage ARCEP : 2025_T4_couv_Metropole_BOUY_4G_data.gpkg
        #                                idx :  0   1    2       3     4   5    6
        parts     = fichier.stem.split("_")
        code_op   = parts[4]
        techno    = parts[5]
        operateur = OPERATEURS.get(code_op, code_op)

        print(f"  -> {operateur} {techno}")
        gdf = gpd.read_file(fichier)

        # Intersection vectorisée entre les polygones ARCEP et les IRIS
        inter = gpd.overlay(
            iris_gdf[["code_iris", "arrondissement", "geometry"]],
            gdf[["niveau", "geometry"]],
            how="intersection",
            keep_geom_type=False,
        )
        inter["inter_area"] = inter.geometry.area

        # Taux de couverture par IRIS = somme des surfaces intersectées / surface IRIS
        taux = (
            inter.groupby("code_iris")["inter_area"].sum()
            .div(iris_surf)
            .mul(100)
            .clip(0, 100)
            .round(2)
        )

        # Niveau dominant = niveau du plus grand fragment d'intersection par IRIS
        niveau = (
            inter.sort_values("inter_area", ascending=False)
            .drop_duplicates("code_iris")
            .set_index("code_iris")["niveau"]
        )

        df_op = iris_gdf[["code_iris", "arrondissement"]].copy()
        df_op["taux_couverture"] = df_op["code_iris"].map(taux).fillna(0)
        df_op["niveau_dominant"] = df_op["code_iris"].map(niveau)
        df_op["score_niveau"]    = df_op["niveau_dominant"].map(NIVEAU_SCORE).fillna(0).astype(int)
        df_op["operateur"]       = operateur
        df_op["techno"]          = techno

        records.append(df_op)

    return pd.concat(records, ignore_index=True)


def compute_densite_antennes(iris_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    # Le fichier OpenData Paris est encodé en cp1252 (Windows-1252), pas UTF-8
    df = pd.read_csv(PATHS["antennes"], sep=";", encoding="cp1252", on_bad_lines="skip")

    df.columns = df.columns.str.strip()
    op_col   = [c for c in df.columns if "rateur" in c.lower()][0]
    arrd_col = [c for c in df.columns if "rondissement" in c.lower()][0]

    df = df.rename(columns={op_col: "operateur", arrd_col: "arrondissement_raw"})
    df["operateur"]     = df["operateur"].str.strip().str.lower().map(OPERATEURS_ANTENNES)
    df = df[df["operateur"].notna()]
    # 75013 → str[-2:] = "13" → int 13
    df["arrondissement"] = df["arrondissement_raw"].astype(str).str[-2:].astype(int)
    df = df[df["arrondissement"].between(1, 20)]

    # Nombre d'antennes par (arrondissement, opérateur)
    antennes_arrd = (
        df.groupby(["arrondissement", "operateur"])
        .size()
        .reset_index(name="nb_antennes_arrd")
    )

    # Nombre d'IRIS par arrondissement - pour distribuer les antennes proportionnellement
    iris_info = iris_gdf[["code_iris", "arrondissement", "surface_m2"]].copy()
    iris_info["surface_km2"] = iris_info["surface_m2"] / 1e6
    nb_iris_arrd = iris_info.groupby("arrondissement").size().reset_index(name="nb_iris")

    antennes_arrd = antennes_arrd.merge(nb_iris_arrd, on="arrondissement", how="left")
    # Distribution uniforme des antennes sur les IRIS de chaque arrondissement
    antennes_arrd["nb_antennes_iris"] = (
        antennes_arrd["nb_antennes_arrd"] / antennes_arrd["nb_iris"]
    ).round(1)

    # Jointure avec les IRIS pour calculer la densité à la surface réelle de chaque IRIS
    densite = iris_info.merge(antennes_arrd, on="arrondissement", how="left")
    densite["nb_antennes"]          = densite["nb_antennes_iris"].fillna(0)
    densite["densite_antennes_km2"] = (densite["nb_antennes"] / densite["surface_km2"]).round(3)

    # Normalisation min-max sur l'ensemble des IRIS Paris
    d_min = densite["densite_antennes_km2"].min()
    d_max = densite["densite_antennes_km2"].max()
    if d_max > d_min:
        densite["score_densite"] = (
            (densite["densite_antennes_km2"] - d_min) / (d_max - d_min) * 100
        ).round(2)
    else:
        densite["score_densite"] = 0.0

    return densite[["code_iris", "operateur", "nb_antennes", "densite_antennes_km2", "score_densite"]]


def build_result(couv_df: pd.DataFrame, densite_df: pd.DataFrame) -> pd.DataFrame:
    couv_4g = couv_df[couv_df["techno"] == "4G"][
        ["code_iris", "arrondissement", "operateur", "taux_couverture", "score_niveau"]
    ].rename(columns={"taux_couverture": "couv_4g", "score_niveau": "score_niveau_4g"})

    couv_5g = couv_df[couv_df["techno"] == "5G"][
        ["code_iris", "operateur", "taux_couverture", "score_niveau"]
    ].rename(columns={"taux_couverture": "couv_5g", "score_niveau": "score_niveau_5g"})

    merged = couv_4g.merge(couv_5g, on=["code_iris", "operateur"], how="outer")

    # On retient le meilleur niveau entre 4G et 5G pour la zone
    merged["score_niveau"] = merged[["score_niveau_4g", "score_niveau_5g"]].max(axis=1).fillna(0)
    merged["couv_4g"]      = merged["couv_4g"].fillna(0)
    merged["couv_5g"]      = merged["couv_5g"].fillna(0)

    merged = merged.merge(
        densite_df[["code_iris", "operateur", "nb_antennes", "densite_antennes_km2", "score_densite"]],
        on=["code_iris", "operateur"],
        how="left",
    )
    merged["score_densite"] = merged["score_densite"].fillna(0)

    # Score_Mobile = 0.10 * 4G + 0.25 * 5G + 0.25 * niveau + 0.40 * densité
    # La couverture théorique est 100% sur tout Paris → peu discriminante.
    # La densité d'antennes (réelle par IRIS) est le vrai facteur différenciateur.
    merged["score_mobile"] = (
        0.10 * merged["couv_4g"]
        + 0.25 * merged["couv_5g"]
        + 0.25 * merged["score_niveau"]
        + 0.40 * merged["score_densite"]
    ).round(2)

    merged = merged.drop(columns=["score_niveau_4g", "score_niveau_5g"], errors="ignore")
    merged["created_at"] = datetime.now()
    return merged.sort_values(["code_iris", "score_mobile"], ascending=[True, False])


def run(engine):
    print("[silver.reseau_mobile] Chargement contours IRIS Paris...")
    iris = load_iris()
    print(f"[silver.reseau_mobile] {len(iris)} IRIS charges")

    print("[silver.reseau_mobile] Calcul couverture theorique (overlay spatial IRIS)...")
    couv = compute_couverture(iris)

    print("[silver.reseau_mobile] Calcul densite antennes par IRIS...")
    densite = compute_densite_antennes(iris)

    result = build_result(couv, densite)

    schema   = "silver"
    inserted = insert_if_empty(result, "reseau_mobile", engine, schema)
    if inserted:
        print(f"[silver.reseau_mobile] {len(result)} lignes inserees")
    else:
        print("[silver.reseau_mobile] table deja remplie, aucune insertion")
