import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]  # on remonte de 3 niveaux

DATA_DIR = BASE_DIR / "data" / "raw" / "environnement"


def get_engine_sql_alchemy():

    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = os.environ["DB_PORT"]
    DB_NAME = os.environ["DB_NAME"]

    # psycopg2
    # engine = create_engine(
    #     f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # )
    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    return engine


def charger_et_nettoyer_donnees():

    df_arbres = pd.read_csv(DATA_DIR / "les-arbres.csv", sep=";")

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


def main():
    df = charger_et_nettoyer_donnees()
    engine = get_engine_sql_alchemy()

    with engine.begin() as connection:

        sql_data = pd.read_sql("SELECT id FROM silver.arbres", con=connection)

        # on insère que les données qui ne sont pas déjà présentes dans la table

        df_merge = df.merge(sql_data, on="id", how="left", indicator=True, suffixes=("", "_sql"))
        df_to_insert = df_merge[df_merge["_merge"] == "left_only"].drop(columns=["_merge"])

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
