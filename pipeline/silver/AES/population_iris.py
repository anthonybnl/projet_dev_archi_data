import pandas as pd
from pipeline.config import PATHS
from pipeline.db import insert_if_empty


def run(engine):
    df = pd.read_csv(PATHS["population_iris"], sep=";", encoding="utf-8", dtype=str)

    # Filtrer sur Paris (code IRIS commence par 751)
    df = df[df["IRIS"].str.startswith("751")].copy()

    df["pop_totale"] = pd.to_numeric(df["P22_POP"], errors="coerce")
    df["pop_3_10"] = (
        pd.to_numeric(df["P22_POP0305"], errors="coerce").fillna(0)
        + pd.to_numeric(df["P22_POP0610"], errors="coerce").fillna(0)
    )
    df["pop_11_17"] = pd.to_numeric(df["P22_POP1117"], errors="coerce")

    # Arrondissement : code IRIS Paris = 751AAIIII, AA = positions [3:5]
    df["arrondissement"] = df["IRIS"].str[3:5].astype(int)
    df = df.rename(columns={"IRIS": "code_iris"})

    result = df[["code_iris", "arrondissement", "pop_totale", "pop_3_10", "pop_11_17"]].dropna()

    inserted = insert_if_empty(result, "population_iris", engine, "silver")
    if inserted:
        print(f"[silver.population_iris] {len(result)} IRIS insérés")
    else:
        print(f"[silver.population_iris] table déjà remplie, aucune insertion")
