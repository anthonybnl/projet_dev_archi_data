import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import json
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

    df_espaces_verts = pd.read_csv(
        DATA_DIR / "environnement" / "espaces_verts.csv", sep=";"
    )

    df_espaces_verts = df_espaces_verts[
        [
            "Identifiant espace vert",
            "Nom de l'espace vert",
            "Code postal",
            "Superficie totale réelle",
            "Année de l'ouverture",
            "Geo Shape",
        ]
    ]

    df_espaces_verts = df_espaces_verts.rename(
        columns={
            "Identifiant espace vert": "id",
            "Nom de l'espace vert": "nom",
            "Code postal": "code_postal",
            "Superficie totale réelle": "superficie",
            "Année de l'ouverture": "annee",
            "Geo Shape": "geo_shape",
        }
    )

    # on filtre sur les NA
    columns_to_check = ["id", "code_postal", "geo_shape"]
    df_espaces_verts = df_espaces_verts.dropna(subset=columns_to_check, how="any")

    # valeurs abérentes : année 9999, on les remplace par des NA
    df_espaces_verts.loc[df_espaces_verts["annee"] == 9999, "annee"] = None

    # valeurs absentes : on les remplace par la médiane
    annee_mediane = df_espaces_verts["annee"].median()
    df_espaces_verts.loc[df_espaces_verts["annee"].isna(), "annee"] = annee_mediane

    return df_espaces_verts


def charger_iris():
    gdf_iris = gpd.read_file(DATA_DIR / "map" / "iris.geojson")

    gdf_iris = gdf_iris[gdf_iris["insee_com"].astype(str).str.startswith("751")]

    gdf_iris = gdf_iris[["code_iris", "geometry"]]

    if gdf_iris.crs and gdf_iris.crs.to_epsg() != 4326:
        print(f"CRS actuel : {gdf_iris.crs}, reprojection en EPSG:4326...")
        gdf_iris = gdf_iris.to_crs(epsg=4326)

    return gdf_iris


def main():
    print("=== Pipeline Silver - Espaces Verts ===")
    gdf_iris = charger_iris()

    print(f"IRIS chargés : {len(gdf_iris)}")

    df = charger_et_nettoyer_donnees()

    print(f"Données espaces verts chargées et nettoyées : {len(df)}")

    # Conversion de la colonne geo_shape (GeoJSON string) en geometry shapely
    df["geometry"] = df["geo_shape"].apply(lambda s: shape(json.loads(s)))
    gdf_ev = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    # Jointure spatiale
    gdf_joined = gpd.sjoin(gdf_ev, gdf_iris, how="left", predicate="intersects")

    df = pd.DataFrame(gdf_joined.drop(columns=["geometry", "index_right"]))

    nb_sans_iris = df["code_iris"].isna().sum()
    print(f"Espaces verts sans IRIS : {nb_sans_iris}")
    print(f"Lignes après jointure (avec dédoublons IRIS) : {len(df)}")

    # on retire ceux qui n'ont pas d'IRIS
    df = df[df["code_iris"].notna()]

    engine = get_engine_sql_alchemy()

    with engine.begin() as connection:

        sql_data = pd.read_sql("SELECT id FROM silver.espaces_verts", con=connection)

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
                "espaces_verts",
                con=connection,
                if_exists="append",
                index=False,
                schema="silver",
            )
            print("Données insérées dans la table 'espaces_verts'")
        else:
            print("Aucune nouvelle donnée à insérer dans la table 'espaces_verts'")


if __name__ == "__main__":
    main()
