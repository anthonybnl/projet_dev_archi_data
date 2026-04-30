
import json
import pandas as pd
from sqlalchemy import text


COUCHES_DISPO = {
    "espaces_verts": {
        "query": "SELECT id as code, nom, geo_shape FROM silver.espaces_verts",
        "geo_type": "raw",  # geo_shape déjà au format GeoJSON
    },
    "colleges": {
        "query": "SELECT id as code, nom, lat, lon FROM silver.colleges_paris",
        "geo_type": "point",
    },
    "gares": {
        "query": "SELECT gare_id as code, ligne || ' - ' || nom as nom, lat, lon FROM silver.map_gares",
        "geo_type": "point",
    },
}


def _point_geojson(lat, lon):
    return {"type": "Point", "coordinates": [lon, lat]}


def get_couche(engine, nom: str) -> list[dict]:
    config = COUCHES_DISPO[nom]

    with engine.connect() as conn:
        df = pd.read_sql(text(config["query"]), conn)

    if config["geo_type"] == "point":
        df = df.dropna(subset=["lat", "lon"])
        df["geo_shape"] = df.apply(lambda r: _point_geojson(r["lat"], r["lon"]), axis=1)
        df = df.drop(columns=["lat", "lon"])
    else:
        # geo_shape stocké en string JSON dans la base
        df["geo_shape"] = df["geo_shape"].apply(lambda s: json.loads(s) if isinstance(s, str) else s)

    return df.to_dict(orient="records")