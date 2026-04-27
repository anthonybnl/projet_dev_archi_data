import pandas as pd
from datetime import datetime
from pipeline.config import PATHS
from pipeline.db import insert_ignore
from pipeline.silver.iris_utils import join_iris


def _parse_arrondissement(val):
    """Convertit '11ème Ardt' → 11"""
    return int(str(val).split("è")[0].split("e")[0].split("r")[0].strip())


def _parse_coords(geo_point):
    """Extrait lat, lon depuis '48.86, 2.38'"""
    try:
        lat, lon = str(geo_point).split(",")
        return float(lat.strip()), float(lon.strip())
    except Exception:
        return None, None


def run(engine):
    df = pd.read_csv(PATHS["colleges"], sep=";", encoding="utf-8-sig")

    # Dernière année disponible
    derniere_annee = df["Année scolaire"].max()
    df = df[df["Année scolaire"] == derniere_annee]

    # Extraire coordonnées
    coords = df["geo_point_2d"].apply(_parse_coords)
    df["lat"] = coords.apply(lambda x: x[0])
    df["lon"] = coords.apply(lambda x: x[1])

    # Extraire numéro arrondissement
    df["arrondissement"] = df["Arrondissement"].apply(_parse_arrondissement)

    result = df[["Libellé établissement", "Adresse", "arrondissement", "lat", "lon"]].copy()
    result.columns = ["nom", "adresse", "arrondissement", "lat", "lon"]
    result = result.dropna(subset=["lat", "lon"])

    # Construire l'id unique : adresse + arrondissement (ex: "101 AVENUE DE LA REPUBLIQUE 11e")
    result["id"] = result["adresse"].str.strip() + " " + result["arrondissement"].astype(str) + "e"

    # Déduplication côté Python
    result = result.drop_duplicates(subset=["id"], keep="first")

    # Jointure spatiale IRIS
    result = join_iris(result)
    result["created_at"] = datetime.now()

    result = result[["id", "nom", "adresse", "arrondissement", "lat", "lon", "code_iris", "nom_iris", "created_at"]]

    schema = "silver"
    insert_ignore(result, "colleges_paris", engine, schema)
    print(f"[silver.colleges_paris] {len(result)} collèges traités (année {derniere_annee})")
