import geopandas as gpd
import pandas as pd
from pipeline.config import IRIS_PATH


def charger_iris():
    gdf_iris = gpd.read_file(IRIS_PATH)

    gdf_iris = gdf_iris[gdf_iris["insee_com"].astype(str).str.startswith("751")]

    gdf_iris = gdf_iris[["code_iris", "nom_iris", "insee_com", "geometry"]]

    if gdf_iris.crs and gdf_iris.crs.to_epsg() != 4326:
        print(f"CRS actuel : {gdf_iris.crs}, reprojection en EPSG:4326...")
        gdf_iris = gdf_iris.to_crs(epsg=4326)

    return gdf_iris


def join_iris(df, lat_col="lat", lon_col="lon"):
    """Jointure spatiale avec les zones IRIS Paris.

    Ajoute code_iris, nom_iris et arrondissement à partir des coordonnées GPS.
    Les lignes hors Paris obtiennent NULL sur ces trois colonnes.
    """
    gdf_points = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs="EPSG:4326"
    )

    gdf_iris = charger_iris()

    joined = gpd.sjoin(
        gdf_points,
        gdf_iris[["code_iris", "nom_iris", "insee_com", "geometry"]],
        how="left",
        predicate="within",
    )
    
    joined["code_iris"] = pd.to_numeric(joined["code_iris"], errors="coerce")
    joined["nom_iris"] = joined["nom_iris"]
    joined["arrondissement_iris"] = pd.to_numeric(
        joined["insee_com"], errors="coerce"
    ).apply(
        lambda x: int(x) - 75100 if pd.notna(x) and 75101 <= int(x) <= 75120 else None
    )

    return pd.DataFrame(
        joined.drop(columns=["insee_com", "geometry", "index_right"], errors="ignore")
    )
