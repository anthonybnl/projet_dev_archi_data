import geopandas as gpd
import pandas as pd
from datetime import datetime
from pipeline.config import PATHS
from pipeline.db import insert_ignore
from pipeline.silver.iris_utils import join_iris


def _parse_coords(val):
    """Extrait lat, lon depuis '48.855907, 2.392570'"""
    try:
        lat, lon = str(val).split(",")
        return float(lat.strip()), float(lon.strip())
    except Exception:
        return None, None


def run(engine):
    # --- Charger les gares IDF ---
    df = pd.read_csv(PATHS["gares"], sep=";", encoding="utf-8-sig")
    df = df[df["idf"] == 1].copy()

    coords = df["Geo Point"].apply(_parse_coords)
    df["lat"] = coords.apply(lambda x: x[0])
    df["lon"] = coords.apply(lambda x: x[1])
    df = df.dropna(subset=["lat", "lon"])

    gdf_gares = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326"
    )

    joined = join_iris(df, lat_col="lat", lon_col="lon")

    result = joined[
        [
            "gares_id",
            "nom_long",
            "mode",
            "res_com",
            "exploitant",
            "lat",
            "lon",
            "code_iris",
            "nom_iris",
            "arrondissement_iris",
        ]
    ].copy()

    result.columns = [
        "gare_id",
        "nom",
        "mode",
        "ligne",
        "exploitant",
        "lat",
        "lon",
        "code_iris",
        "nom_iris",
        "arrondissement",
    ]

    result["gare_id"] = pd.to_numeric(result["gare_id"], errors="coerce")
    result = result.dropna(subset=["gare_id"])
    result["gare_id"] = result["gare_id"].astype(int)

    # Garder uniquement les gares à Paris (arrondissement non null)
    result = result[result["arrondissement"].notna()]
    result["arrondissement"] = result["arrondissement"].astype(int)

    result = result.drop_duplicates(subset=["gare_id"], keep="first")
    result["created_at"] = datetime.now()

    schema = "silver"
    insert_ignore(result, "map_gares", engine, schema)
    print(f"[silver.map_gares] {len(result)} gares traitées")
    print(f"  → Gares avec IRIS: {result['code_iris'].notna().sum()}")
    print(f"  → Gares Paris: {result['arrondissement'].notna().sum()}")
