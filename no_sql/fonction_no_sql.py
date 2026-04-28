"""
Utilitaires de connexion et d'insertion pour MongoDB.
Ce module est utilisé par les scripts de chargement NoSQL du projet.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# On charge le .env depuis la racine du projet (un cran au-dessus de ce fichier)
_env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(_env_path)


def get_mongo_client():
    """
    Ouvre une connexion vers le MongoDB local lancé via Docker.
    Les credentials sont lus depuis le fichier .env du projet.
    """
    host = os.getenv("DB_HOST_MONGODB", "localhost")
    port = int(os.getenv("DB_PORT_MONGODB", 27017))
    user = os.getenv("DB_USER_MONGODB", "root")
    password = os.getenv("DB_PASSWORD_MONGODB", "")

    # Format URI standard pour une instance MongoDB avec authentification
    uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
    return MongoClient(uri)


def get_database(client=None):
    """
    Retourne l'objet base de données MongoDB configuré dans le .env.
    Si aucun client n'est fourni, une nouvelle connexion est ouverte.
    """
    if client is None:
        client = get_mongo_client()
    db_name = os.getenv("DB_NAME_MONGODB", "urban_data")
    return client[db_name]


def load_collection(db, collection_name, documents):
    """
    Remplace intégralement une collection par une nouvelle liste de documents.

    On repart toujours d'une collection vide pour garantir la cohérence des données
    (pas de doublons si le script est relancé plusieurs fois).
    """
    collection = db[collection_name]

    # Suppression des données existantes avant rechargement
    collection.drop()

    # Insertion en bloc, cela est plus rapide qu'un insert ligne par ligne
    result = collection.insert_many(documents)
    return len(result.inserted_ids)
