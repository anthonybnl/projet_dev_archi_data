import geopandas as gpd
import pandas as pd
from pipeline.config import PATHS


def join_iris(df, lat_col="lat", lon_col="lon"):
    """Jointure spatiale avec les zones IRIS Paris.

    Ajoute code_iris, nom_iris et arrondissement à partir des coordonnées GPS.
    Les lignes hors Paris obtiennent NULL sur ces trois colonnes.
    """
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
        crs="EPSG:4326"
    )

    df_iris = pd.read_csv(PATHS["iris"], sep=";", encoding="utf-8-sig")
    df_iris = df_iris[df_iris["DEP"] == 75].copy()
    df_iris["geometry"] = df_iris["Geo Shape"].apply(lambda x: __import__("shapely").from_geojson(x))
    gdf_iris = gpd.GeoDataFrame(df_iris, geometry="geometry", crs="EPSG:4326")

    joined = gpd.sjoin(
        gdf_points,
        gdf_iris[["CODE_IRIS", "NOM_IRIS", "INSEE_COM", "geometry"]],
        how="left",
        predicate="within"
    )

    joined["code_iris"] = pd.to_numeric(joined["CODE_IRIS"], errors="coerce")
    joined["nom_iris"] = joined["NOM_IRIS"]
    joined["arrondissement_iris"] = pd.to_numeric(joined["INSEE_COM"], errors="coerce").apply(
        lambda x: int(x) - 75100 if pd.notna(x) and 75101 <= int(x) <= 75120 else None
    )

    return joined.drop(columns=["CODE_IRIS", "NOM_IRIS", "INSEE_COM", "geometry", "index_right"], errors="ignore")
