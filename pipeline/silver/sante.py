import pandas as pd
from datetime import datetime
from pipeline.config import PATHS, LAYERS
from pipeline.db import insert_if_empty

BPE_COLS = {
    "codgeo": 0,
    "nb_centres_sante": 9,   # D108
    "nb_medecins": 34,        # D265
    "nb_infirmiers": 50,      # D281
    "nb_pharmacies": 55,      # D307
}


def run(engine):
    df = pd.read_excel(
        PATHS["bpe_sante"],
        sheet_name="ARM",
        header=None,
        skiprows=10,
    )

    # Garder uniquement les colonnes utiles
    df = df.iloc[:, list(BPE_COLS.values())].copy()
    df.columns = list(BPE_COLS.keys())

    # Filtrer Paris (751xx)
    df = df[df["codgeo"].astype(str).str.startswith("751")].dropna(subset=["codgeo"])

    # Extraire numéro d'arrondissement (75101 → 1)
    df["arrondissement"] = df["codgeo"].astype(str).str[3:].astype(int)

    for col in ["nb_centres_sante", "nb_medecins", "nb_infirmiers", "nb_pharmacies"]:
        df[col] = df[col].fillna(0).round(0).astype(int)

    result = df[["arrondissement", "nb_medecins", "nb_infirmiers", "nb_centres_sante", "nb_pharmacies"]].copy()
    result["created_at"] = datetime.now()

    schema = LAYERS["silver_schema"]
    inserted = insert_if_empty(result, "sante_paris", engine, schema)
    if inserted:
        print(f"[silver.sante_paris] {len(result)} arrondissements insérés")
    else:
        print(f"[silver.sante_paris] table déjà remplie, aucune insertion")
