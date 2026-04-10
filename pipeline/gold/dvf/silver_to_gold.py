import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from sqlalchemy import text
from db import engine


def agreger_par_iris():
    df = pd.read_sql("SELECT * FROM silver.dvf", engine)
    print(f"silver.dvf : {len(df)} lignes lues")

    sans_iris = df["code_iris"].isna().sum()
    if sans_iris > 0:
        print(f"  {sans_iris} lignes sans code_iris — exclues de gold")

    df = df[df["code_iris"].notna()].copy()

    # on a besoin de la surface pour calculer le prix au m²
    # on exclut les lignes sans surface ou avec surface = 0
    df = df[df["surface_reelle_bati"].notna() & (df["surface_reelle_bati"] > 0)].copy()
    df = df[df["valeur_fonciere"].notna() & (df["valeur_fonciere"] > 0)].copy()

    df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]
    df["annee"] = pd.to_datetime(df["date_mutation"]).dt.year

    # on agrège par IRIS et année
    gold = df.groupby(["code_iris", "annee", "arrondissement"]).agg(
        nb_transactions=("id_mutation", "count"),
        prix_m2_median=("prix_m2", "median"),
        prix_m2_moyen=("prix_m2", "mean"),
        nb_appartements=("type_local", lambda x: (x == "Appartement").sum()),
        nb_maisons=("type_local", lambda x: (x == "Maison").sum()),
    ).reset_index()

    # on arrondit les prix pour ne pas avoir 15 décimales
    gold["prix_m2_median"] = gold["prix_m2_median"].round(2)
    gold["prix_m2_moyen"] = gold["prix_m2_moyen"].round(2)

    print(f"gold : {len(gold)} lignes ({gold['code_iris'].nunique()} IRIS, {gold['annee'].nunique()} années)")
    return gold


def upsert_gold(gold):
    upsert_sql = text("""
        INSERT INTO gold.indicateurs_dvf_iris
            (code_iris, annee, arrondissement, nb_transactions, prix_m2_median, prix_m2_moyen, nb_appartements, nb_maisons)
        VALUES
            (:code_iris, :annee, :arrondissement, :nb_transactions, :prix_m2_median, :prix_m2_moyen, :nb_appartements, :nb_maisons)
        ON CONFLICT (code_iris, annee) DO UPDATE SET
            arrondissement = EXCLUDED.arrondissement,
            nb_transactions = EXCLUDED.nb_transactions,
            prix_m2_median = EXCLUDED.prix_m2_median,
            prix_m2_moyen = EXCLUDED.prix_m2_moyen,
            nb_appartements = EXCLUDED.nb_appartements,
            nb_maisons = EXCLUDED.nb_maisons
    """)

    with engine.begin() as conn:
        for _, row in gold.iterrows():
            conn.execute(upsert_sql, {
                "code_iris": row["code_iris"],
                "annee": int(row["annee"]),
                "arrondissement": int(row["arrondissement"]),
                "nb_transactions": int(row["nb_transactions"]),
                "prix_m2_median": float(row["prix_m2_median"]),
                "prix_m2_moyen": float(row["prix_m2_moyen"]),
                "nb_appartements": int(row["nb_appartements"]),
                "nb_maisons": int(row["nb_maisons"]),
            })

    print(f"gold.indicateurs_dvf_iris : {len(gold)} lignes upsertées")


def run():
    gold = agreger_par_iris()
    if len(gold) == 0:
        print("rien à insérer dans gold")
        return
    upsert_gold(gold)


if __name__ == "__main__":
    run()
