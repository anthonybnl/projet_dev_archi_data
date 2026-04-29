"""
Lancement : uvicorn api.main:app --reload-dir api --reload --port 8000
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if not str(ROOT) in sys.path:
    sys.path.insert(0, str(ROOT))


from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sqlalchemy import text
from pipeline.db import get_engine
from api.geo import get_arrondissements_geojson, get_iris_geojson
from api.indicateurs import get_indicateurs_iris, get_indicateurs_arrondissement

app = FastAPI(
    title="Urban Data Explorer — API indicateurs",
    description="Expose les données gold (DVF, Filosofi, RPLS) au front",
)

# on autorise le front local (Vite tourne sur :5173 par défaut)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# endpoints GeoJSON depuis MongoDB

@app.get("/api/geo/arrondissements")
def get_arrondissements_geo():
    """Retourne le GeoJSON des 20 arrondissements de Paris depuis MongoDB."""
    return get_arrondissements_geojson()


@app.get("/api/geo/iris")
def get_iris_geo():
    """Retourne le GeoJSON des zones IRIS de Paris depuis MongoDB."""
    return get_iris_geojson()


# endpoints indicateurs depuis PostgreSQL

@app.get("/api/indicateurs/iris")
def indicateurs_iris(annee: int = Query(2025)):
    return get_indicateurs_iris(annee)


@app.get("/api/indicateurs/arrondissement")
def indicateurs_arrondissement(annee: int = Query(2025)):
    return get_indicateurs_arrondissement(annee)
