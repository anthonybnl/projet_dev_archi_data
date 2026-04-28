import pandas as pd
from datetime import datetime
from pipeline.config import PATHS
from pipeline.db import insert_ignore
from pipeline.silver.iris_utils import join_iris


def run(engine):
    df = pd.read_csv(PATHS["hopitaux"], sep=";", encoding="utf-8-sig")

    df = df[df["CP_VILLE"].astype(str).str.startswith("75")].copy()
    df["arrondissement"] = df["CP_VILLE"].astype(str).str[:5].astype(int) - 75000

    result = df[
        [
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
        ]
    ].copy()
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

    # Jointure spatiale IRIS
    result = join_iris(result)
    result["created_at"] = datetime.now()

    schema = "silver"
    result = result[
        [
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
            "code_iris",
            "nom_iris",
            "created_at",
        ]
    ]

    insert_ignore(result, "map_sante", engine, schema)
    print(f"[silver.map_sante] {len(result)} établissements traités")
    print(
        f"  → Top catégories : {pd.Series(result['categorie'].values).value_counts().head(5).to_dict()}"
    )
    print(f"  → Sans code_iris : {result['code_iris'].isna().sum()}")
