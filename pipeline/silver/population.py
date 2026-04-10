import pandas as pd
from datetime import datetime
from pipeline.config import PATHS
from pipeline.db import insert_if_empty


def run(engine):
    schema = "silver"
    _run_population_enfants(engine, schema)
    _run_population_totale(engine, schema)


def _run_population_enfants(engine, schema):
    df = pd.read_excel(PATHS["age_insee"], sheet_name="COM")

    # Filtrer les arrondissements parisiens (75101 → 75120)
    df["INSEE"] = pd.to_numeric(df["INSEE"], errors="coerce")
    df = df[df["INSEE"].between(75101, 75120)].copy()

    # Pop 3-10 ans = F3-5 + F6-10 + H3-5 + H6-10
    df["pop_3_10"] = df["F3-5"] + df["F6-10"] + df["H3-5"] + df["H6-10"]
    # Pop 11-17 ans = F11-17 + H11-17
    df["pop_11_17"] = df["F11-17"] + df["H11-17"]

    # Extraire numéro d'arrondissement depuis le code INSEE (75101 → 1)
    df["arrondissement"] = df["INSEE"] - 75100

    result = df[["arrondissement", "pop_3_10", "pop_11_17"]].copy()
    result["pop_3_10"] = result["pop_3_10"].round(0).astype(int)
    result["pop_11_17"] = result["pop_11_17"].round(0).astype(int)
    result["created_at"] = datetime.now()

    inserted = insert_if_empty(result, "population_enfants_paris", engine, schema)
    if inserted:
        print(f"[silver.population_enfants_paris] {len(result)} arrondissements insérés")
    else:
        print(f"[silver.population_enfants_paris] table déjà remplie, aucune insertion")


def _run_population_totale(engine, schema):
    df = pd.read_csv(PATHS["population"], encoding="utf-8-sig")

    def extract_arr(nom):
        parts = str(nom).replace("er", "").replace("ème", "").replace("e", "").split()
        for p in parts:
            if p.isdigit():
                return int(p)
        return None

    df["arrondissement"] = df["Arrondissement"].apply(extract_arr)
    df = df.rename(columns={"Population": "population_totale"})
    result = df[["arrondissement", "population_totale"]].dropna()
    result["arrondissement"] = result["arrondissement"].astype(int)
    result["created_at"] = datetime.now()

    inserted = insert_if_empty(result, "population_totale_paris", engine, schema)
    if inserted:
        print(f"[silver.population_totale_paris] {len(result)} arrondissements insérés")
    else:
        print(f"[silver.population_totale_paris] table déjà remplie, aucune insertion")
