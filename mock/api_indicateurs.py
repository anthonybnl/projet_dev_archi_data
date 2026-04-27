"""
API FastAPI pour exposer les indicateurs du marché du logement parisien au front.

Endpoints :
  GET /api/geo/arrondissements         → GeoJSON des 20 arrondissements
  GET /api/geo/iris                    → GeoJSON des IRIS de Paris
  GET /api/indicateurs/arrondissement  → indicateurs agrégés par arrondissement
  GET /api/indicateurs/iris            → indicateurs au niveau IRIS

Lance avec :
  uvicorn mock.api_indicateurs:app --reload --port 8000

Prérequis : les tables gold doivent être remplies (lancer les pipelines avant).
"""

import json
import sys
from pathlib import Path

# on remonte au dossier projet pour pouvoir importer pipeline/db.py
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sqlalchemy import text
from db import get_engine

app = FastAPI(
    title="Urban Data Explorer — API indicateurs",
    description="Expose les données gold (DVF, Filosofi, RPLS) au front",
)

# on autorise le front local (Vite tourne sur :5173 par défaut)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── chemins vers les fichiers GeoJSON statiques ────────────────────────────
ARRONDISSEMENTS_GEOJSON = ROOT / "data" / "raw" /"map" / "arrondissements.geojson"
IRIS_GEOJSON_FRANCE = ROOT / "data" / "raw" /"map" / "iris.geojson"

# on met en cache les geojson en mémoire (chargés une fois au démarrage)
_arr_geo = None
_iris_geo = None


def charger_arrondissements():
    global _arr_geo
    if _arr_geo is None:
        with open(ARRONDISSEMENTS_GEOJSON, encoding="utf-8") as f:
            _arr_geo = json.load(f)
    return _arr_geo


def charger_iris_paris():
    """Charge le geojson France entière et filtre sur Paris (codes commune 751xx)."""
    global _iris_geo
    if _iris_geo is None:
        with open(IRIS_GEOJSON_FRANCE, encoding="utf-8") as f:
            full = json.load(f)
        # on filtre features dont le code commune commence par 751
        features_paris = []
        for f in full["features"]:
            props = f.get("properties", {})
            code_com = str(props.get("insee_com") or props.get("INSEE_COM") or "")
            if code_com.startswith("751"):
                features_paris.append(f)
        _iris_geo = {"type": "FeatureCollection", "features": features_paris}
    return _iris_geo


# ─── endpoints geojson ──────────────────────────────────────────────────────
@app.get("/api/geo/arrondissements")
def get_arrondissements_geo():
    return charger_arrondissements()


@app.get("/api/geo/iris")
def get_iris_geo():
    return charger_iris_paris()


# ─── endpoints indicateurs ──────────────────────────────────────────────────

# requête SQL principale : on JOIN les 3 tables gold sur (code_iris, annee)
# avec FULL OUTER pour garder même les IRIS qui n'ont pas toutes les données
SQL_IRIS = """
WITH dvf AS (
    SELECT code_iris, annee, arrondissement, prix_m2_median, nb_transactions
    FROM gold.indicateurs_dvf_iris
    WHERE annee = :annee
),
soc AS (
    SELECT code_iris, annee, arrondissement, nb_logements_sociaux_finances
    FROM gold.indicateurs_logements_sociaux_iris
    WHERE annee = :annee
),
filo AS (
    SELECT code_iris, annee, arrondissement, revenu_median, iai
    FROM gold.indicateurs_socio_eco_iris
    WHERE annee = :annee
)
SELECT
    COALESCE(dvf.code_iris, soc.code_iris, filo.code_iris) AS code_iris,
    COALESCE(dvf.arrondissement, soc.arrondissement, filo.arrondissement) AS arrondissement,
    dvf.prix_m2_median AS price,
    soc.nb_logements_sociaux_finances AS social,
    filo.revenu_median AS income,
    filo.iai AS iai
FROM dvf
FULL OUTER JOIN soc ON dvf.code_iris = soc.code_iris
FULL OUTER JOIN filo ON COALESCE(dvf.code_iris, soc.code_iris) = filo.code_iris
"""


def fetch_iris(annee: int) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(SQL_IRIS), conn, params={"annee": annee})
    return df


@app.get("/api/indicateurs/iris")
def get_indicateurs_iris(annee: int = Query(2025)):
    df = fetch_iris(annee)
    if df.empty:
        return []

    # on enrichit avec un nom lisible (basé sur le geojson IRIS)
    iris_geo = charger_iris_paris()
    noms = {}
    for f in iris_geo["features"]:
        p = f.get("properties", {})
        code = str(p.get("code_iris") or p.get("CODE_IRIS") or "")
        nom = p.get("nom_iris") or p.get("NOM_IRIS") or code
        noms[code] = nom

    out = []
    for _, row in df.iterrows():
        code = str(row["code_iris"])
        out.append({
            "code": code,
            "name": noms.get(code, code),
            "arrondissement": int(row["arrondissement"]) if pd.notna(row["arrondissement"]) else 0,
            "price":  None if pd.isna(row["price"])  else float(row["price"]),
            "social": None if pd.isna(row["social"]) else int(row["social"]),
            "income": None if pd.isna(row["income"]) else float(row["income"]),
            "iai":    None if pd.isna(row["iai"])    else float(row["iai"]),
        })
    return out


@app.get("/api/indicateurs/arrondissement")
def get_indicateurs_arrondissement(annee: int = Query(2025)):
    """Agrégation des indicateurs IRIS au niveau arrondissement.

    - prix m² : moyenne pondérée par nb_transactions (plus représentatif)
    - logements sociaux : somme
    - revenu médian : moyenne (les revenus médians IRIS sont déjà des médianes)
    - iai : moyenne
    """
    df = fetch_iris(annee)
    if df.empty:
        return []

    # on récupère aussi nb_transactions pour la pondération du prix
    # → on relance une requête plus simple pour ça
    engine = get_engine()
    with engine.connect() as conn:
        df_w = pd.read_sql(
            text("SELECT arrondissement, prix_m2_median, nb_transactions FROM gold.indicateurs_dvf_iris WHERE annee = :a"),
            conn, params={"a": annee},
        )

    # moyenne pondérée du prix par arrondissement
    if not df_w.empty:
        df_w = df_w.dropna(subset=["prix_m2_median", "nb_transactions"])
        df_w["w_price"] = df_w["prix_m2_median"] * df_w["nb_transactions"]
        prix_par_arr = (
            df_w.groupby("arrondissement").agg(
                w=("w_price", "sum"),
                n=("nb_transactions", "sum"),
            )
        )
        prix_par_arr["price"] = prix_par_arr["w"] / prix_par_arr["n"]
        prix_par_arr = prix_par_arr["price"].to_dict()
    else:
        prix_par_arr = {}

    # agrégations simples sur le reste
    agg = df.groupby("arrondissement").agg(
        social=("social", "sum"),
        income=("income", "mean"),
        iai=("iai", "mean"),
    ).reset_index()

    out = []
    for _, row in agg.iterrows():
        arr = int(row["arrondissement"])
        if arr == 0:
            continue
        # code arrondissement INSEE = 75100 + numéro (1 → 75101)
        code_insee = f"751{arr:02d}"
        out.append({
            "code": code_insee,
            "name": f"{arr}{'er' if arr == 1 else 'e'} arrondissement",
            "arrondissement": arr,
            "price":  None if arr not in prix_par_arr else float(prix_par_arr[arr]),
            "social": None if pd.isna(row["social"]) else int(row["social"]),
            "income": None if pd.isna(row["income"]) else float(row["income"]),
            "iai":    None if pd.isna(row["iai"])    else float(row["iai"]),
        })
    return out


@app.get("/")
def root():
    return {
        "name": "Urban Data Explorer API",
        "endpoints": [
            "/api/geo/arrondissements",
            "/api/geo/iris",
            "/api/indicateurs/arrondissement?annee=2025",
            "/api/indicateurs/iris?annee=2025",
        ],
    }
