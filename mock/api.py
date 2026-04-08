import datetime
import json
import numpy as np
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI

load_dotenv()

# données
DATA_DIR = Path.cwd() / "data"
GEOJSON_PATH = DATA_DIR / "arrondissements.geojson"

arrondissements_geojson: dict

with open(GEOJSON_PATH) as f:
    arrondissements_geojson = json.load(f)


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


@app.get("/features/")
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
