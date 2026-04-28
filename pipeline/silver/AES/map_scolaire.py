import pandas as pd
import geopandas as gpd
from datetime import datetime
from pipeline.config import PATHS, IRIS_PATH
from pipeline.db import insert_ignore
from pipeline.silver.iris_utils import join_iris


def _parse_coords(geo_point):
    try:
        lat, lon = str(geo_point).split(",")
        return float(lat.strip()), float(lon.strip())
    except Exception:
        return None, None


def _parse_arrondissement(val):
    try:
        return int(str(val).split("è")[0].split("e")[0].split("r")[0].strip())
    except Exception:
        return None


def _load_file(path):
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    derniere_annee = df["Année scolaire"].dropna().max()
    df = df[df["Année scolaire"] == derniere_annee]
    coords = df["geo_point_2d"].apply(_parse_coords)
    df["lat"] = coords.apply(lambda x: x[0])
    df["lon"] = coords.apply(lambda x: x[1])
    df["arrondissement"] = df["Arrondissement"].apply(_parse_arrondissement)
    return df[["Libellé établissement", "Adresse", "Type établissement", "arrondissement", "lat", "lon"]].copy()


def _load_iris():
    gdf = gpd.read_file(IRIS_PATH)
    gdf = gdf[gdf["insee_com"].astype(str).str.startswith("751")][["code_iris", "geometry"]]
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf


def run(engine):
    df_elem = _load_file(PATHS["elementaires"])
    df_mat = _load_file(PATHS["maternelles"])

    # Déduplication des Polyvalents : supprimés de elementaires, conservés depuis maternelles
    poly_mat = df_mat[df_mat["Type établissement"] == "Polyvalent"].set_index(
        ["Libellé établissement", "Adresse"]
    ).index
    df_elem = df_elem[
        ~df_elem.set_index(["Libellé établissement", "Adresse"]).index.isin(poly_mat)
    ]

    result = pd.concat([df_elem, df_mat], ignore_index=True)
    result.columns = ["nom", "adresse", "type", "arrondissement", "lat", "lon"]
    result = result.dropna(subset=["lat", "lon", "arrondissement"])
    result["arrondissement"] = result["arrondissement"].astype(int)
    result["id"] = result["adresse"].str.strip() + " " + result["arrondissement"].astype(str) + "e"
    result = result.drop_duplicates(subset=["id"], keep="first")

    # Jointure spatiale IRIS
    result = join_iris(result)
    result["created_at"] = datetime.now()
    result = result[["id", "nom", "adresse", "type", "arrondissement", "lat", "lon", "code_iris", "created_at"]]

    result = result[["id", "nom", "adresse", "type", "arrondissement", "lat", "lon", "code_iris", "nom_iris", "created_at"]]

    schema = "silver"
    insert_ignore(result, "map_scolaire", engine, schema)
    print(f"[silver.map_scolaire] {len(result)} établissements traités")
    print(f"  → Répartition : {pd.Series(result['type'].values).value_counts().to_dict()}")
    print(f"  → Sans code_iris : {result['code_iris'].isna().sum()}")
