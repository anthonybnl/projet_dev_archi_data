import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
from sqlalchemy import text
from pipeline.db import get_engine


def _normalize(series: pd.Series) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.0, index=series.index)
    return (series - mn) / (mx - mn)


def calculer_arrondissement(engine):
    df_effectifs = pd.read_sql(
        "SELECT arrondissement, SUM(nb_eleves) AS nb_eleves FROM silver.elementaires_maternelles_effectifs GROUP BY arrondissement",
        engine,
    )
    df_pop_enfants = pd.read_sql(
        "SELECT arrondissement, pop_3_10, pop_11_17 FROM silver.population_enfants_paris",
        engine,
    )
    df_pop_totale = pd.read_sql(
        "SELECT arrondissement, population_totale FROM silver.population_totale_paris",
        engine,
    )
    df_colleges = pd.read_sql(
        "SELECT arrondissement, COUNT(*) AS nb_colleges FROM silver.colleges_paris GROUP BY arrondissement",
        engine,
    )
    df_sante = pd.read_sql(
        "SELECT arrondissement, nb_medecins, nb_infirmiers, nb_pharmacies FROM silver.sante_paris",
        engine,
    )
    df_map_sante = pd.read_sql(
        "SELECT arrondissement, COUNT(*) AS nb_centres_hospitaliers FROM silver.map_sante GROUP BY arrondissement",
        engine,
    )

    # Base : 20 arrondissements
    df = df_pop_enfants.merge(df_pop_totale, on="arrondissement")
    df = df.merge(df_effectifs, on="arrondissement", how="left")
    df = df.merge(df_colleges, on="arrondissement", how="left")
    df = df.merge(df_sante, on="arrondissement", how="left")
    df = df.merge(df_map_sante, on="arrondissement", how="left")

    df["nb_colleges"] = df["nb_colleges"].fillna(0)

    # Indicateurs bruts
    df["e1_scolarisation"]      = df["nb_eleves"] / df["pop_3_10"].replace(0, float("nan"))
    df["e2_couverture_college"] = df["nb_colleges"] / df["pop_11_17"].replace(0, float("nan"))

    pop = df["population_totale"].replace(0, float("nan"))
    df["s1_medecins"]               = df["nb_medecins"]             / pop * 10_000
    df["s2_infirmiers"]             = df["nb_infirmiers"]           / pop * 10_000
    df["s4_pharmacies"]             = df["nb_pharmacies"]           / pop * 10_000
    df["nb_centres_hospitaliers"]   = df["nb_centres_hospitaliers"].fillna(0)
    df["s3_centres_hospitaliers"]   = df["nb_centres_hospitaliers"] / pop * 10_000

    # Normalisation min-max sur les 20 arrondissements
    df["norm_e1"] = _normalize(df["e1_scolarisation"])
    df["norm_e2"] = _normalize(df["e2_couverture_college"])
    df["norm_s1"] = _normalize(df["s1_medecins"].fillna(0))
    df["norm_s2"] = _normalize(df["s2_infirmiers"].fillna(0))
    df["norm_s3"] = _normalize(df["s3_centres_hospitaliers"].fillna(0))
    df["norm_s4"] = _normalize(df["s4_pharmacies"].fillna(0))

    df["score_education"] = (2 * df["norm_e1"] + df["norm_e2"]) / 3
    df["score_sante"]     = (df["norm_s1"] + df["norm_s2"] + df["norm_s3"] + df["norm_s4"]) / 4
    df["score_aes"]       = (df["score_education"] + df["score_sante"]) / 2

    result = df[[
        "arrondissement",
        "e1_scolarisation", "e2_couverture_college",
        "s1_medecins", "s2_infirmiers", "s3_centres_hospitaliers", "s4_pharmacies",
        "score_education", "score_sante", "score_aes",
    ]]

    print(f"[gold.arrondissement] {len(result)} arrondissements — score_aes moyen = {result['score_aes'].mean():.3f}")
    return result


def upsert_gold(engine, df):
    upsert_sql = text("""
        INSERT INTO gold.indicateurs_aes_arrondissement (
            arrondissement,
            e1_scolarisation, e2_couverture_college,
            s1_medecins, s2_infirmiers, s3_centres_hospitaliers, s4_pharmacies,
            score_education, score_sante, score_aes
        ) VALUES (
            :arrondissement,
            :e1_scolarisation, :e2_couverture_college,
            :s1_medecins, :s2_infirmiers, :s3_centres_hospitaliers, :s4_pharmacies,
            :score_education, :score_sante, :score_aes
        )
        ON CONFLICT (arrondissement) DO UPDATE SET
            e1_scolarisation          = EXCLUDED.e1_scolarisation,
            e2_couverture_college     = EXCLUDED.e2_couverture_college,
            s1_medecins               = EXCLUDED.s1_medecins,
            s2_infirmiers             = EXCLUDED.s2_infirmiers,
            s3_centres_hospitaliers   = EXCLUDED.s3_centres_hospitaliers,
            s4_pharmacies             = EXCLUDED.s4_pharmacies,
            score_education           = EXCLUDED.score_education,
            score_sante               = EXCLUDED.score_sante,
            score_aes                 = EXCLUDED.score_aes
    """)

    def _float(v):
        try:
            return float(v) if v == v else None
        except Exception:
            return None

    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(upsert_sql, {
                "arrondissement":          int(row["arrondissement"]),
                "e1_scolarisation":        _float(row["e1_scolarisation"]),
                "e2_couverture_college":   _float(row["e2_couverture_college"]),
                "s1_medecins":               _float(row["s1_medecins"]),
                "s2_infirmiers":             _float(row["s2_infirmiers"]),
                "s3_centres_hospitaliers":   _float(row["s3_centres_hospitaliers"]),
                "s4_pharmacies":             _float(row["s4_pharmacies"]),
                "score_education":           _float(row["score_education"]),
                "score_sante":             _float(row["score_sante"]),
                "score_aes":               _float(row["score_aes"]),
            })

    print(f"gold.indicateurs_aes_arrondissement : {len(df)} lignes upsertées")


def run(engine):
    df = calculer_arrondissement(engine)
    if df.empty:
        print("rien à insérer dans gold AES arrondissement")
        return
    upsert_gold(engine, df)
