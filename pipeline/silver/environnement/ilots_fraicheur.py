import json

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import geopandas as gpd
from shapely.geometry import shape


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[3]  # on remonte de 3 niveaux

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

    df_ilots = pd.read_csv(
        DATA_DIR / "environnement" / "ilots-de-fraicheur-equipements-activites.csv",
        sep=";",
    )

    df_ilots = df_ilots[["IDENTIFIANT", "Nom", "Code postal", "geo_shape"]]

    df_ilots = df_ilots.rename(
        columns={
            "IDENTIFIANT": "id",
            "Nom": "nom",
            "Code postal": "code_postal",
            "geo_shape": "geo_shape",
        }
    )

    return df_ilots


def charger_iris():
    gdf_iris = gpd.read_file(DATA_DIR / "map" / "iris.geojson")

    gdf_iris = gdf_iris[gdf_iris["insee_com"].astype(str).str.startswith("751")]

    gdf_iris = gdf_iris[["code_iris", "geometry"]]

    if gdf_iris.crs and gdf_iris.crs.to_epsg() != 4326:
        print(f"CRS actuel : {gdf_iris.crs}, reprojection en EPSG:4326...")
        gdf_iris = gdf_iris.to_crs(epsg=4326)

    return gdf_iris


def main():
    print("=== Pipeline Silver - Ilots de Fraicheur ===")
    gdf_iris = charger_iris()

    print(f"IRIS chargés : {len(gdf_iris)}")

    df = charger_et_nettoyer_donnees()

    print(f"Données ilots chargées et nettoyées : {len(df)}")

    # on transforme en GeoDataFrame
    df["geometry"] = df["geo_shape"].apply(lambda s: shape(json.loads(s)))

    gdf_ilots = gpd.GeoDataFrame(
        df,
        geometry="geometry",
        crs="EPSG:4326",
    )

    gdf_joined = gpd.sjoin(gdf_ilots, gdf_iris, how="left", predicate="within")

    df = pd.DataFrame(gdf_joined.drop(columns=["geometry", "index_right"]))

    print(f"Ilots avec code_iris manquant : {df['code_iris'].isna().sum()}")

    df = df[df["code_iris"].notna()]

    print(f"Données après suppression code_iris manquant : {len(df)}")

    engine = get_engine_sql_alchemy()

    with engine.begin() as connection:

        sql_data = pd.read_sql(
            "SELECT id, code_postal FROM silver.ilots_fraicheur", con=connection
        )

        # on insère que les données qui ne sont pas déjà présentes dans la table

        # jointure sur (id, code_postal) car id n'est pas unique dans la table (ex : MU75)
        df_merge = df.merge(
            sql_data,
            on=["id", "code_postal"],
            how="left",
            indicator=True,
            suffixes=("", "_sql"),
        )
        df_to_insert = df_merge[df_merge["_merge"] == "left_only"].drop(
            columns=["_merge"]
        )

        if not df_to_insert.empty:
            print(f"Données à insérer : {len(df_to_insert)}")
            df_to_insert.to_sql(
                "ilots_fraicheur",
                con=connection,
                if_exists="append",
                index=False,
                schema="silver",
            )
            print("Données insérées dans la table 'ilots_fraicheur'")
        else:
            print("Aucune nouvelle donnée à insérer dans la table 'ilots_fraicheur'")


if __name__ == "__main__":
    main()
