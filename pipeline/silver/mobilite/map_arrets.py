import geopandas as gpd
import pandas as pd
from datetime import datetime
from pipeline.config import PATHS
from pipeline.db import insert_ignore

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

    gdf_arrets = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326"
    )

    # --- Charger les IRIS Paris ---
    df_iris = pd.read_csv(PATHS["iris"], sep=";", encoding="utf-8-sig")
    df_iris = df_iris[df_iris["DEP"] == 75].copy()
    df_iris["geometry"] = df_iris["Geo Shape"].apply(lambda x: __import__("shapely").from_geojson(x))
    gdf_iris = gpd.GeoDataFrame(df_iris, geometry="geometry", crs="EPSG:4326")

    # --- Jointure spatiale : arrêt → IRIS ---
    joined = gpd.sjoin(gdf_arrets, gdf_iris[["CODE_IRIS", "NOM_IRIS", "INSEE_COM", "geometry"]], how="left", predicate="within")

    # Extraire l'arrondissement depuis INSEE_COM (75106 → 6)
    joined["arrondissement"] = pd.to_numeric(joined["INSEE_COM"], errors="coerce")
    joined["arrondissement"] = joined["arrondissement"].apply(
        lambda x: int(x) - 75100 if pd.notna(x) and 75101 <= int(x) <= 75120 else None
    )

    result = joined[[
        "ArRId",
        "ArRName",
        "ArRType",
        "lat",
        "lon",
        "CODE_IRIS",
        "NOM_IRIS",
        "arrondissement",
    ]].copy()

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
