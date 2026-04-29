import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_path)


def get_mongo_uri():
    MONGO_HOST = os.environ["DB_HOST_MONGODB"]
    MONGO_PORT = int(os.environ["DB_PORT_MONGODB"])
    MONGO_USER = os.environ["DB_USER_MONGODB"]
    MONGO_PASSWORD = os.environ["DB_PASSWORD_MONGODB"]
    MONGO_DB_NAME = os.environ["DB_NAME_MONGODB"]

    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

    return MONGO_URI, MONGO_DB_NAME


def _get_db():
    mongo_uri, mongo_db_name = get_mongo_uri()
    client = MongoClient(mongo_uri)
    return client[mongo_db_name]
