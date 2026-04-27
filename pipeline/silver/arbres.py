import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import geopandas as gpd

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]  # on remonte de 3 niveaux
DATA_DIR = BASE_DIR / "data" / "raw"


def get_engine_sql_alchemy():

    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = os.environ["DB_PORT"]
    DB_NAME = os.environ["DB_NAME"]

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # psycopg2
    # engine = create_engine(
    #     f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # )
    engine = create_engine(DATABASE_URL)

    return engine


def charger_et_nettoyer_donnees():

    df_arbres = pd.read_csv(DATA_DIR / "environnement" / "les-arbres.csv", sep=";")

    # filtre sur Paris
    df = df_arbres[df_arbres["ARRONDISSEMENT"].str.startswith("PARIS")]

    # on split geo_point_2d en latitude et longitude
    df[["latitude", "longitude"]] = (
        df["geo_point_2d"].str.split(",", expand=True).astype(float)
    )

    # nettoyage arrondissement : que le numéro
    df["ARRONDISSEMENT"] = (
        df["ARRONDISSEMENT"]
        .str.replace("PARIS ", "")
        .str.replace("ARRDT", "")
        .str.replace("ER", "")
        .str.replace("E", "")
        .astype(int)
    )

    # on ne garde que les colonnes utiles
    df = df[["IDBASE", "ARRONDISSEMENT", "latitude", "longitude"]]

    df = df.rename(
        columns={
            "IDBASE": "id",
            "ARRONDISSEMENT": "arrondissement",
        }
    )

    return df


def charger_iris():
    gdf_iris = gpd.read_file(DATA_DIR / "map" / "iris.geojson")

    gdf_iris = gdf_iris[gdf_iris["insee_com"].astype(str).str.startswith("751")]

    gdf_iris = gdf_iris[["code_iris", "geometry"]]

    if gdf_iris.crs and gdf_iris.crs.to_epsg() != 4326:
        print(f"CRS actuel : {gdf_iris.crs}, reprojection en EPSG:4326...")
        gdf_iris = gdf_iris.to_crs(epsg=4326)

    return gdf_iris


def main():
    print("=== Pipeline Silver - Arbres ===")
    gdf_iris = charger_iris()

    print(f"IRIS chargés : {len(gdf_iris)}")

    df = charger_et_nettoyer_donnees()

    print(f"Données arbres chargées et nettoyées : {len(df)}")

    # consolidation avec le code_iris
    gdf_arbres = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    )

    gdf_joined = gpd.sjoin(gdf_arbres, gdf_iris, how="left", predicate="within")

    df = gdf_joined[
        ["id", "arrondissement", "latitude", "longitude", "code_iris"]
    ].copy()

    print(f"Arbres avec code_iris manquant : {df['code_iris'].isna().sum()}")

    df = pd.DataFrame(df)

    engine = get_engine_sql_alchemy()

    with engine.begin() as connection:

        sql_data = pd.read_sql("SELECT id FROM silver.arbres", con=connection)

        # on insère que les données qui ne sont pas déjà présentes dans la table

        df_merge = df.merge(
            sql_data, on="id", how="left", indicator=True, suffixes=("", "_sql")
        )
        df_to_insert = df_merge[df_merge["_merge"] == "left_only"].drop(
            columns=["_merge"]
        )

        if not df_to_insert.empty:
            print(f"Données à insérer : {len(df_to_insert)}")
            df_to_insert.to_sql(
                "arbres",
                con=connection,
                if_exists="append",
                index=False,
                schema="silver",
            )
            print("Données insérées dans la table 'arbres'")
        else:
            print("Aucune nouvelle donnée à insérer dans la table 'arbres'")


if __name__ == "__main__":
    main()
