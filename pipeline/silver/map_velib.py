import pandas as pd
import geopandas as gpd
import json
from datetime import datetime
from shapely.geometry import Point
from pipeline.config import PATHS, LAYERS
from pipeline.db import insert_ignore


def _parse_coords(val):
    """Extrait lat, lon depuis '48.855907555969, 2.3925706744194'"""
    try:
        lat, lon = str(val).split(",")
        return float(lat.strip()), float(lon.strip())
    except Exception:
        return None, None


def run(engine):
    # --- Charger les stations Vélib ---
    df = pd.read_csv(PATHS["velib"], sep=";", encoding="utf-8-sig")

    coords = df["Coordonnées géographiques"].apply(_parse_coords)
    df["lat"] = coords.apply(lambda x: x[0])
    df["lon"] = coords.apply(lambda x: x[1])
    df = df.dropna(subset=["lat", "lon"])

    # Créer un GeoDataFrame des stations
    gdf_stations = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326"
    )

    # --- Charger les IRIS Paris ---
    df_iris = pd.read_csv(PATHS["iris"], sep=";", encoding="utf-8-sig")
    df_iris = df_iris[df_iris["DEP"] == 75].copy()

    # Construire la géométrie des polygones IRIS depuis le GeoJSON
    df_iris["geometry"] = df_iris["Geo Shape"].apply(lambda x: __import__("shapely").from_geojson(x))
    gdf_iris = gpd.GeoDataFrame(df_iris, geometry="geometry", crs="EPSG:4326")

    # --- Jointure spatiale : station → IRIS ---
    joined = gpd.sjoin(gdf_stations, gdf_iris[["CODE_IRIS", "NOM_IRIS", "INSEE_COM", "geometry"]], how="left", predicate="within")

    # Extraire l'arrondissement depuis INSEE_COM (75101 → 1)
    joined["arrondissement"] = pd.to_numeric(joined["INSEE_COM"], errors="coerce")
    joined["arrondissement"] = joined["arrondissement"].apply(
        lambda x: int(x) - 75100 if pd.notna(x) and 75101 <= int(x) <= 75120 else None
    )

    result = joined[[
        "Identifiant station",
        "Nom de la station",
        "Capacité de la station",
        "lat",
        "lon",
        "CODE_IRIS",
        "NOM_IRIS",
        "arrondissement",
    ]].copy()

    result.columns = [
        "station_id",
        "nom",
        "capacite",
        "lat",
        "lon",
        "code_iris",
        "nom_iris",
        "arrondissement",
    ]

    result["station_id"] = result["station_id"].astype(str)

    # Garder uniquement les stations à Paris (arrondissement non null)
    result = result[result["arrondissement"].notna()]
    result["arrondissement"] = result["arrondissement"].astype(int)

    result = result.drop_duplicates(subset=["station_id"], keep="first")
    result["created_at"] = datetime.now()

    schema = LAYERS["silver_schema"]
    insert_ignore(result, "map_velib", engine, schema)
    print(f"[silver.map_velib] {len(result)} stations traitées")
    print(f"  → Stations avec IRIS: {result['code_iris'].notna().sum()}")
    print(f"  → Stations Paris: {result['arrondissement'].notna().sum()}")
