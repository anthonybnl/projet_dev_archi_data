import datetime
import json
import numpy as np
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI
import pandas as pd

load_dotenv()

# données
DATA_DIR = Path.cwd() / "data"
GEOJSON_PATH = DATA_DIR / "arrondissements.geojson"

arrondissements_geojson: dict

with open(GEOJSON_PATH) as f:
    arrondissements_geojson = json.load(f)

df_arbres = pd.read_csv(DATA_DIR / "raw" / "environnement" / "les-arbres.csv", sep=";")
df_espaces_verts = pd.read_csv(
    DATA_DIR / "raw" / "environnement" / "espaces_verts.csv", sep=";"
)


np.random.seed(int(datetime.datetime.now().timestamp()))

# api


app = FastAPI(
    title="API Pour notre projet",
    description="Description API",
)

# CORS

# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_methods=["*"],
# )


@app.get("/arrondissements/")
async def get_features():
    return arrondissements_geojson


@app.get("/scores/")
async def get_scores():
    rand_environnement = np.random.rand(20).tolist()
    rand_mobilite = np.random.rand(20).tolist()

    values = [
        {
            "environnement": i1,
            "mobilite": i2,
            "score": (i1 + i2) / 2,
        }
        for i1, i2 in zip(rand_environnement, rand_mobilite)
    ]

    result = dict(zip(range(1, 21), values))

    return result


@app.get("/environnement/arbres")
async def get_environnement_arbres():
    data = df_arbres

    res = []
    for _, row in data.iterrows():
        latlng = row["geo_point_2d"].split(", ")
        res.append(
            {
                "id": row["IDBASE"],
                "arr": row["ARRONDISSEMENT"],
                "geo_point_2d": {"lat": float(latlng[0]), "lon": float(latlng[1])},
            }
        )

    return res


@app.get("/environnement/espaces_verts")
async def get_environnement_espaces_verts():
    data = df_espaces_verts[df_espaces_verts["Identifiant espace vert"].notna()]

    feature_collection = []

    for _, row in data.iterrows():

        feature = {"type": "Feature"}

        id = int(row["Identifiant espace vert"])

        if pd.isna(row["Nom de l'espace vert"]):
            nom = None
        else:
            nom = row["Nom de l'espace vert"]

        if pd.isna(row["Code postal"]):
            code_postal = None
        else:
            code_postal = int(row["Code postal"])

        if pd.isna(row["Superficie totale réelle"]):
            superficie = None
        else:
            superficie = float(row["Superficie totale réelle"])

        if pd.isna(row["Geo Shape"]):
            geo_shape = None
        else:
            geo_shape = json.loads(row["Geo Shape"])

        if geo_shape is not None:
            feature["geometry"] = geo_shape
            feature["properties"] = {
                "id": id,
                "nom": nom,
                "code_postal": code_postal,
                "superficie": superficie,
            }
            feature_collection.append(feature)
            
    return {"type": "FeatureCollection", "features": feature_collection}
