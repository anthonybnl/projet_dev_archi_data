import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from sqlalchemy import text
from db import engine


def calculer_iai():
    df_filo = pd.read_sql("SELECT * FROM silver.filosofi", engine)
    print(f"silver.filosofi : {len(df_filo)} lignes lues")

    df_dvf = pd.read_sql("SELECT * FROM gold.indicateurs_dvf_iris", engine)
    print(f"gold.indicateurs_dvf_iris : {len(df_dvf)} lignes lues")

    if len(df_dvf) == 0:
        print("la table gold DVF est vide — lancer d'abord le pipeline DVF")
        return pd.DataFrame()

    # on fusionne Filosofi et DVF sur (code_iris, annee)
    # les années Filosofi (2018-2021) matchent avec les années DVF si elles existent
    gold = df_filo.merge(
        df_dvf[["code_iris", "annee", "prix_m2_median"]],
        on=["code_iris", "annee"],
        how="inner",
    )

    nb_match = len(gold)
    print(f"  {nb_match} croisements IRIS×année entre Filosofi et DVF")

    if nb_match == 0:
        # si pas de match exact sur l'année, on fait un cross-join
        # parce que les années Filosofi et DVF ne se chevauchent pas forcément
        print("  pas de match direct — on croise chaque année DVF avec le Filosofi le plus proche")
        gold = croiser_annees_proches(df_filo, df_dvf)

    if len(gold) == 0:
        return pd.DataFrame()

    # on ne garde que les lignes où on a les deux valeurs
    gold = gold[gold["revenu_median"].notna() & gold["prix_m2_median"].notna()].copy()

    # IAI = prix_m2_median / revenu_median_mensuel
    # on divise le revenu annuel par 12 pour avoir le mensuel
    gold["iai"] = (gold["prix_m2_median"] / (gold["revenu_median"] / 12)).round(4)

    gold = gold[["code_iris", "annee", "arrondissement", "revenu_median", "prix_m2_median", "iai"]]

    print(f"gold : {len(gold)} lignes avec IAI calculé")
    print(f"  IAI moyen = {gold['iai'].mean():.2f}, médian = {gold['iai'].median():.2f}")
    return gold


def croiser_annees_proches(df_filo, df_dvf):
    """Pour chaque année DVF, on prend le Filosofi de l'année la plus proche."""
    annees_filo = sorted(df_filo["annee"].unique())
    resultats = []

    for _, row_dvf in df_dvf.iterrows():
        annee_dvf = row_dvf["annee"]
        # on trouve l'année Filosofi la plus proche
        annee_filo = min(annees_filo, key=lambda a: abs(a - annee_dvf))

        filo_match = df_filo[
            (df_filo["code_iris"] == row_dvf["code_iris"]) &
            (df_filo["annee"] == annee_filo)
        ]

        if len(filo_match) > 0:
            resultats.append({
                "code_iris": row_dvf["code_iris"],
                "annee": annee_dvf,
                "arrondissement": row_dvf["arrondissement"],
                "revenu_median": filo_match.iloc[0]["revenu_median"],
                "prix_m2_median": row_dvf["prix_m2_median"],
            })

    if not resultats:
        return pd.DataFrame()

    gold = pd.DataFrame(resultats)
    print(f"  {len(gold)} croisements par année la plus proche")
    return gold


def upsert_gold(gold):
    upsert_sql = text("""
        INSERT INTO gold.indicateurs_socio_eco_iris
            (code_iris, annee, arrondissement, revenu_median, prix_m2_median, iai)
        VALUES
            (:code_iris, :annee, :arrondissement, :revenu_median, :prix_m2_median, :iai)
        ON CONFLICT (code_iris, annee) DO UPDATE SET
            arrondissement = EXCLUDED.arrondissement,
            revenu_median = EXCLUDED.revenu_median,
            prix_m2_median = EXCLUDED.prix_m2_median,
            iai = EXCLUDED.iai
    """)

    with engine.begin() as conn:
        for _, row in gold.iterrows():
            conn.execute(upsert_sql, {
                "code_iris": row["code_iris"],
                "annee": int(row["annee"]),
                "arrondissement": int(row["arrondissement"]),
                "revenu_median": float(row["revenu_median"]),
                "prix_m2_median": float(row["prix_m2_median"]),
                "iai": float(row["iai"]),
            })

    print(f"gold.indicateurs_socio_eco_iris : {len(gold)} lignes upsertées")


def run():
    gold = calculer_iai()
    if len(gold) == 0:
        print("rien à insérer dans gold")
        return
    upsert_gold(gold)


if __name__ == "__main__":
    run()
