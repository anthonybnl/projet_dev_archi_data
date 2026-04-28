import pandas as pd
import geopandas as gpd
from datetime import datetime
from pipeline.config import PATHS, IRIS_PATH
from pipeline.db import insert_ignore
from pipeline.silver.iris_utils import join_iris


def _parse_arrondissement(val):
    return int(str(val).split("è")[0].split("e")[0].split("r")[0].strip())


def _parse_coords(geo_point):
    try:
        lat, lon = str(geo_point).split(",")
        return float(lat.strip()), float(lon.strip())
    except Exception:
        return None, None


def _load_iris():
    gdf = gpd.read_file(IRIS_PATH)
    gdf = gdf[gdf["insee_com"].astype(str).str.startswith("751")][["code_iris", "geometry"]]
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf


def run(engine):
    df = pd.read_csv(PATHS["colleges"], sep=";", encoding="utf-8-sig")

    derniere_annee = df["Année scolaire"].max()
    df = df[df["Année scolaire"] == derniere_annee]

    coords = df["geo_point_2d"].apply(_parse_coords)
    df["lat"] = coords.apply(lambda x: x[0])
    df["lon"] = coords.apply(lambda x: x[1])
    df["arrondissement"] = df["Arrondissement"].apply(_parse_arrondissement)

    result = df[["Libellé établissement", "Adresse", "arrondissement", "lat", "lon"]].copy()
    result.columns = ["nom", "adresse", "arrondissement", "lat", "lon"]
    result = result.dropna(subset=["lat", "lon"])
    result["id"] = result["adresse"].str.strip() + " " + result["arrondissement"].astype(str) + "e"
    result = result.drop_duplicates(subset=["id"], keep="first")

    # Jointure spatiale IRIS
    result = join_iris(result)
    result["created_at"] = datetime.now()
    result = result[["id", "nom", "adresse", "arrondissement", "lat", "lon", "code_iris", "created_at"]]

    result = result[["id", "nom", "adresse", "arrondissement", "lat", "lon", "code_iris", "nom_iris", "created_at"]]

    schema = "silver"
    insert_ignore(result, "colleges_paris", engine, schema)
    print(f"[silver.colleges_paris] {len(result)} collèges traités (année {derniere_annee})")
    print(f"  → Sans code_iris : {result['code_iris'].isna().sum()}")
