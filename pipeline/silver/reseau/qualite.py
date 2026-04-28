import json
import warnings
from datetime import datetime

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

from pipeline.config import PATHS
from pipeline.db import insert_if_empty

warnings.filterwarnings("ignore")

# Paris = code INSEE commune 75056
PARIS_INSEE = 75056

DEBIT_MAX_REF = 100.0   # 100 Mbps = score 100

OPERATEUR_MAP = {
    "bouygues": "Bouygues",
    "bouygue":  "Bouygues",
    "free":     "Free",
    "orange":   "Orange",
    "sfr":      "SFR",
}


def normalise_operateur(s: str) -> str:
    if pd.isna(s):
        return None
    s_low = str(s).lower().strip()
    for key, val in OPERATEUR_MAP.items():
        if key in s_low:
            return val
    return str(s).strip().title()


def load_iris() -> gpd.GeoDataFrame:
    with open(PATHS["iris_geojson"], encoding="utf-8") as f:
        geojson = json.load(f)

    rows = []
    for feat in geojson["features"]:
        props = feat["properties"]
        if props.get("dep") != "75":
            continue
        insee_com = int(props["insee_com"])
        rows.append({
            "code_iris":      props["code_iris"],
            "arrondissement": insee_com - 75100,
            "geometry":       shape(feat["geometry"]),
        })

    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    return gdf.to_crs("EPSG:2154")


def sjoin_iris(df: pd.DataFrame, lat_col: str, lon_col: str,
               iris_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """Associe chaque mesure à son IRIS via ses coordonnées WGS84."""
    df = df.copy()
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])

    gdf_pts = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2154")

    joined = gpd.sjoin(
        gdf_pts,
        iris_gdf[["code_iris", "arrondissement", "geometry"]],
        how="left",
        predicate="within",
    )
    return pd.DataFrame(joined.drop(columns="geometry"))


def load_qos(iris_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    df = pd.read_csv(
        PATHS["qos_habitations"], sep=";", encoding="latin-1",
        on_bad_lines="skip", low_memory=False,
    )

    df["insee_com"] = pd.to_numeric(df["insee_com"], errors="coerce")
    df_paris = df[df["insee_com"] == PARIS_INSEE].copy()

    if len(df_paris) == 0:
        print("[silver.reseau_qualite] Aucune donnee Paris dans le fichier QoS")
        return pd.DataFrame(columns=["code_iris", "arrondissement", "operateur",
                                     "bitrate_dl", "result_ok"])

    df_paris["operateur"] = df_paris["operator"].apply(normalise_operateur)

    # bitrate_dl : les décimales peuvent être encodées avec une virgule (format FR)
    df_paris["bitrate_dl"] = (
        df_paris["bitrate_dl"].astype(str).str.replace(",", ".", regex=False)
    )
    df_paris["bitrate_dl"] = pd.to_numeric(df_paris["bitrate_dl"], errors="coerce")

    # Fiabilité : 1 si la mesure est un succès, 0 sinon
    df_paris["result_ok"] = (df_paris["Result"] == "Success").astype(int)

    joined = sjoin_iris(df_paris, "latitude_start", "longitude_start", iris_gdf)
    joined = joined.dropna(subset=["code_iris"])

    return joined[["code_iris", "arrondissement", "operateur", "bitrate_dl", "result_ok"]]


def run(engine):
    print("[silver.reseau_qualite] Chargement contours IRIS Paris...")
    iris = load_iris()

    print("[silver.reseau_qualite] Chargement QoS ARCEP...")
    qos = load_qos(iris)
    print(f"[silver.reseau_qualite] {len(qos)} mesures Paris chargees")

    if len(qos) == 0:
        print("[silver.reseau_qualite] Aucune donnee - table ignoree")
        return

    # Score débit : médiane normalisée sur 100 Mbps (ref validée projet)
    # Seulement les mesures avec bitrate_dl non nul
    score_debit = (
        qos.dropna(subset=["bitrate_dl"])
        .groupby(["code_iris", "operateur"])["bitrate_dl"]
        .median()
        .div(DEBIT_MAX_REF).mul(100).clip(0, 100).round(2)
        .rename("score_debit")
    )

    # Score fiabilité
    score_fiabilite = (
        qos.groupby(["code_iris", "operateur"])["result_ok"]
        .mean().mul(100).round(2)
        .rename("score_fiabilite")
    )

    result = pd.concat([score_debit, score_fiabilite], axis=1).reset_index()
    result = result.dropna(subset=["code_iris", "operateur"])

    # Score_Qualite = 0.50 * débit + 0.50 * fiabilité
    # La latence est absente du fichier ARCEP pour Paris
    result["score_qualite"] = (
        0.50 * result["score_debit"].fillna(0)
        + 0.50 * result["score_fiabilite"].fillna(0)
    ).round(2)
    result["score_latence"] = None  # conservé dans le schéma pour évolution future

    # Récupération de l'arrondissement depuis le sjoin
    arrd_map = qos[["code_iris", "arrondissement"]].drop_duplicates("code_iris")
    result = result.merge(arrd_map, on="code_iris", how="left")
    result["arrondissement"] = result["arrondissement"].fillna(0).astype(int)

    result["created_at"] = datetime.now()

    schema   = "silver"
    inserted = insert_if_empty(result, "reseau_qualite", engine, schema)
    if inserted:
        print(f"[silver.reseau_qualite] {len(result)} lignes inserees")
    else:
        print("[silver.reseau_qualite] table deja remplie, aucune insertion")
