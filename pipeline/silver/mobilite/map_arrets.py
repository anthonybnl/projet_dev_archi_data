import geopandas as gpd
import pandas as pd
from datetime import datetime
from pipeline.config import PATHS
from pipeline.db import insert_ignore
from pipeline.silver.iris_utils import join_iris

TYPES_RETENUS = {"bus", "cableway"}


def _parse_coords(val):
    """Extrait lat, lon depuis '48.855907, 2.392570'"""
    try:
        lat, lon = str(val).split(",")
        return float(lat.strip()), float(lon.strip())
    except Exception:
        return None, None


def run(engine):
    # --- Charger les arrêts ---
    df = pd.read_csv(PATHS["arrets"], sep=";", encoding="utf-8-sig")

    # Filtre sur bus et cableway uniquement (metro, rail, tram déjà dans map_gares)
    df = df[df["ArRType"].isin(TYPES_RETENUS)].copy()

    coords = df["ArRGeopoint"].apply(_parse_coords)
    df["lat"] = coords.apply(lambda x: x[0])
    df["lon"] = coords.apply(lambda x: x[1])
    df = df.dropna(subset=["lat", "lon"])

    joined = join_iris(df, lat_col="lat", lon_col="lon")

    result = joined[
        [
            "ArRId",
            "ArRName",
            "ArRType",
            "lat",
            "lon",
            "code_iris",
            "nom_iris",
            "arrondissement_iris",
        ]
    ].copy()

    result.columns = [
        "arret_id",
        "nom",
        "type",
        "lat",
        "lon",
        "code_iris",
        "nom_iris",
        "arrondissement",
    ]

    result["arret_id"] = pd.to_numeric(result["arret_id"], errors="coerce")
    result = result.dropna(subset=["arret_id"])
    result["arret_id"] = result["arret_id"].astype(int)

    # Garder uniquement les arrêts à Paris (arrondissement non null)
    result = result[result["arrondissement"].notna()]
    result["arrondissement"] = result["arrondissement"].astype(int)

    result = result.drop_duplicates(subset=["arret_id"], keep="first")
    result["created_at"] = datetime.now()

    schema = "silver"
    insert_ignore(result, "map_arrets", engine, schema)
    print(f"[silver.map_arrets] {len(result)} arrêts traités")
    print(f"  → Par type: {result['type'].value_counts().to_dict()}")
    print(f"  → Arrêts avec IRIS: {result['code_iris'].notna().sum()}")
