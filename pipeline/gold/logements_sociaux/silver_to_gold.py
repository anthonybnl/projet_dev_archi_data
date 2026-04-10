import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from sqlalchemy import text
from db import engine


def agreger_par_iris():
    df = pd.read_sql("SELECT * FROM silver.logements_sociaux", engine)
    print(f"silver.logements_sociaux : {len(df)} lignes lues")

    # on exclut les lignes sans code IRIS — pas de sens géographique pour l'agrégation
    sans_iris = df["code_iris"].isna().sum()
    if sans_iris > 0:
        print(f"  {sans_iris} lignes sans code_iris — exclues de gold")

    df = df[df["code_iris"].notna()].copy()

    # on inclut arrondissement dans le groupby parce qu'un IRIS appartient à un seul arrondissement
    # ça permet de garder l'info sans casser l'agrégation
    gold = df.groupby(["code_iris", "annee_financement", "arrondissement"]).agg(
        nb_logements_sociaux_finances=("nb_logements_finances", "sum"),
        nb_plai=("nb_plai", "sum"),
        nb_plus=("nb_plus", "sum"),
        nb_plus_cd=("nb_plus_cd", "sum"),
        nb_pls=("nb_pls", "sum"),
    ).reset_index()

    gold = gold.rename(columns={"annee_financement": "annee"})
    print(f"gold : {len(gold)} lignes ({gold['code_iris'].nunique()} IRIS, {gold['annee'].nunique()} années)")
    return gold


def upsert_gold(gold):
    """Insert ou update dans gold — si le couple (code_iris, annee) existe déjà, on met à jour les valeurs."""
    # on utilise INSERT ... ON CONFLICT ... DO UPDATE de PostgreSQL
    upsert_sql = text("""
        INSERT INTO gold.indicateurs_logements_sociaux_iris
            (code_iris, annee, arrondissement, nb_logements_sociaux_finances, nb_plai, nb_plus, nb_plus_cd, nb_pls)
        VALUES
            (:code_iris, :annee, :arrondissement, :nb_logements_sociaux_finances, :nb_plai, :nb_plus, :nb_plus_cd, :nb_pls)
        ON CONFLICT (code_iris, annee) DO UPDATE SET
            arrondissement = EXCLUDED.arrondissement,
            nb_logements_sociaux_finances = EXCLUDED.nb_logements_sociaux_finances,
            nb_plai = EXCLUDED.nb_plai,
            nb_plus = EXCLUDED.nb_plus,
            nb_plus_cd = EXCLUDED.nb_plus_cd,
            nb_pls = EXCLUDED.nb_pls
    """)

    with engine.begin() as conn:
        for _, row in gold.iterrows():
            conn.execute(upsert_sql, {
                "code_iris": row["code_iris"],
                "annee": int(row["annee"]),
                "arrondissement": int(row["arrondissement"]),
                "nb_logements_sociaux_finances": int(row["nb_logements_sociaux_finances"]),
                "nb_plai": int(row["nb_plai"]),
                "nb_plus": int(row["nb_plus"]),
                "nb_plus_cd": int(row["nb_plus_cd"]),
                "nb_pls": int(row["nb_pls"]),
            })

    print(f"gold.indicateurs_logements_sociaux_iris : {len(gold)} lignes upsertées")


def run():
    gold = agreger_par_iris()
    if len(gold) == 0:
        print("rien à insérer dans gold")
        return
    upsert_gold(gold)


if __name__ == "__main__":
    run()
