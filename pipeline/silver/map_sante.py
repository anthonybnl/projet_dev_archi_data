import pandas as pd
from datetime import datetime
from pipeline.config import PATHS, LAYERS
from pipeline.db import insert_ignore


def run(engine):
    df = pd.read_csv(PATHS["hopitaux"], sep=";", encoding="utf-8-sig")

    # Filtrer sur Paris (code postal 75xxx)
    df = df[df["CP_VILLE"].astype(str).str.startswith("75")].copy()

    # Extraire l'arrondissement depuis le code postal (ex: 75011 → 11)
    df["arrondissement"] = df["CP_VILLE"].astype(str).str[:5].astype(int) - 75000

    result = df[[
        "FINESS_ET",
        "RAISON_SOCIALE",
        "ADRESSE_COMPLETE",
        "NUM_TEL",
        "CATEGORIE_DE_L_ETABLISSEMENT",
        "TYPE_ETABLISSEMENT",
        "CP_VILLE",
        "arrondissement",
        "lat",
        "lng",
    ]].copy()

    result.columns = [
        "finess",
        "nom",
        "adresse",
        "telephone",
        "categorie",
        "type_etablissement",
        "cp_ville",
        "arrondissement",
        "lat",
        "lon",
    ]

    result = result.dropna(subset=["lat", "lon"])
    result["arrondissement"] = result["arrondissement"].astype(int)
    result["created_at"] = datetime.now()

    schema = LAYERS["silver_schema"]
    insert_ignore(result, "map_sante", engine, schema)
    print(f"[silver.map_sante] {len(result)} établissements traités")
    print(f"  → Top catégories : {result['categorie'].value_counts().head(5).to_dict()}")
