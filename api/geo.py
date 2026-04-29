from api.nosql_db import _get_db


def _collection_to_feature_collection(db, collection_name: str) -> dict:
    cursor = db[collection_name].find({}, {"_id": 0})  # exclure _id
    features = list(cursor)

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def get_arrondissements_geojson() -> dict:
    """Retourne le GeoJSON FeatureCollection des 20 arrondissements de Paris."""
    db = _get_db()
    return _collection_to_feature_collection(db, "arrondissements")


def get_iris_geojson() -> dict:
    """Retourne le GeoJSON FeatureCollection des zones IRIS de Paris."""
    db = _get_db()
    return _collection_to_feature_collection(db, "iris")
