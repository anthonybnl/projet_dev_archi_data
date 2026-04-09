import pandas as pd
from datetime import datetime
from pipeline.config import PATHS, LAYERS
from pipeline.db import insert_ignore


def run(engine):
    df = pd.read_csv(PATHS["nb_classes"], sep=";", encoding="utf-8-sig", low_memory=False)

    # Filtrer Paris et dernière année disponible
    df = df[df["Code département"].astype(str).str.strip() == "75"]
    derniere_annee = df["Rentrée scolaire"].max()
    df = df[df["Rentrée scolaire"] == derniere_annee]

    # Extraire l'arrondissement depuis le Code Postal (ex: 75014 → 14)
    df["arrondissement"] = df["Code Postal"].astype(str).str.strip().astype(int) - 75000

    result = df[[
        "Numéro de l'école",
        "Patronyme",
        "Dénomination principale",
        "Secteur",
        "arrondissement",
        "Nombre total d'élèves",
    ]].copy()

    result.columns = [
        "numero_ecole",
        "nom",
        "type",
        "secteur",
        "arrondissement",
        "nb_eleves",
    ]

    result["nb_eleves"] = result["nb_eleves"].astype(int)
    result["created_at"] = datetime.now()

    schema = LAYERS["silver_schema"]
    insert_ignore(result, "elementaires_maternelles_effectifs", engine, schema)
    print(f"[silver.elementaires_maternelles_effectifs] {len(result)} écoles traitées (année {derniere_annee})")
