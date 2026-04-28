"""
Chargement des données géographiques de Paris dans MongoDB.

Ce script alimente deux collections :
  - arrondissements : les 20 arrondissements de Paris
  - iris : les zones IRIS INSEE couvrant Paris (département 75)

Les géométries sont stockées au format GeoJSON natif, ce qui permet
d'exploiter directement les opérateurs spatiaux MongoDB ($geoWithin, etc.).
"""

import sys
import os

# Ajout de la racine du projet au chemin pour les imports locaux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import geopandas as gpd
from pymongo import GEOSPHERE

from no_sql.fonction_no_sql import get_mongo_client, get_database, load_collection

# Chemins vers les fichiers source
PATH_MAP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'map'))
PATH_ARRONDISSEMENTS = os.path.join(PATH_MAP, 'arrondissements.geojson')
PATH_IRIS = os.path.join(PATH_MAP, 'iris.geojson')


def geojson_to_documents(gdf, id_field=None):
    """
    Chaque document respecte la structure GeoJSON Feature standard :
    { "type": "Feature", "properties": {...}, "geometry": {...} }
    Ce format est reconnu nativement par MongoDB pour les requêtes spatiales.

    Si id_field est fourni, la valeur de ce champ devient le _id du document,
    ce qui garantit l'unicité et simplifie les recherches par identifiant métier.
    """
    documents = []
    for _, row in gdf.iterrows():
        doc = {
            "type": "Feature",
            # Toutes les colonnes non-géométriques vont dans properties
            "properties": {
                col: row[col]
                for col in gdf.columns
                if col != gdf.geometry.name
            },
            # La géométrie au format GeoJSON (dict Python)
            "geometry": row.geometry.__geo_interface__,
        }
        # On utilise l'identifiant métier comme _id pour éviter les doublons
        if id_field:
            doc["_id"] = row[id_field]
        documents.append(doc)
    return documents


def charger_arrondissements(db):
    """
    Charge les 20 arrondissements de Paris dans la collection 'arrondissements'.
    Les données source couvrent uniquement Paris, aucun filtre nécessaire.
    """
    print("Lecture de arrondissements.geojson...")
    gdf = gpd.read_file(PATH_ARRONDISSEMENTS)

    # On s'assure d'être en WGS84,requis pour l'index 2dsphere de MongoDB
    gdf = gdf.to_crs("EPSG:4326")

    # c_arinsee est le code INSEE officiel de l'arrondissement (ex: 75101, 75120)
    documents = geojson_to_documents(gdf, id_field="c_arinsee")
    nb = load_collection(db, "arrondissements", documents)

    # Index spatial pour permettre les requêtes géographiques ($geoWithin, $near, etc.)
    db["arrondissements"].create_index([("geometry", GEOSPHERE)])

    print(f"  -> {nb} arrondissements insérés dans la collection 'arrondissements'.")
    return nb


def charger_iris(db):
    """
    Charge les zones IRIS de Paris dans la collection 'iris'.
    Le fichier source est national (France entière), on filtre sur dep == '75'.
    """
    print("Lecture de iris.geojson (fichier volumineux, patience)...")
    gdf = gpd.read_file(PATH_IRIS)

    # Filtrage sur Paris uniquement,le fichier source contient toute la France
    gdf_paris = gdf[gdf["dep"] == "75"].copy()

    # Reprojection en WGS84 si nécessaire
    gdf_paris = gdf_paris.to_crs("EPSG:4326")

    # code_iris est l'identifiant unique de chaque zone IRIS (ex: 751010205)
    documents = geojson_to_documents(gdf_paris, id_field="code_iris")
    nb = load_collection(db, "iris", documents)

    # Index spatial pour les requêtes géographiques sur les zones IRIS
    db["iris"].create_index([("geometry", GEOSPHERE)])

    print(f"  -> {nb} zones IRIS insérées dans la collection 'iris'.")
    return nb


if __name__ == "__main__":
    print("=== Chargement des données géographiques dans MongoDB ===\n")

    client = get_mongo_client()
    db = get_database(client)

    print(f"Connecté à la base : {db.name}\n")

    charger_arrondissements(db)
    charger_iris(db)

    client.close()
    print("\nChargement terminé. Vérification possible via Mongo Express : http://localhost:8081")
