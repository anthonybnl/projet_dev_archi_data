import math
import pandas as pd
from sqlalchemy import text
from pipeline.db import get_engine
from api.geo import _get_db


def _sanitize(records: list[dict]) -> list[dict]:
    """Remplace les float NaN/inf par None pour la sérialisation JSON."""
    for row in records:
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                row[k] = None
    return records


def _get_iris_referentiel():
    """Récupère la liste complète des IRIS Paris depuis MongoDB."""
    db = _get_db()
    docs = db["iris"].find({}, {"_id": 1, "properties.insee_com": 1})

    rows = []
    for doc in docs:
        code_iris = str(doc["_id"])
        insee_com = doc.get("properties", {}).get("insee_com", "")
        # arrondissement = 2 derniers chiffres du code commune (75101 -> 1)
        arr = int(str(insee_com)[-2:]) if insee_com else None
        rows.append({"code_iris": code_iris, "arrondissement": arr})

    return pd.DataFrame(rows)


def _resolve_annee(engine, table, schema, annee_cible):
    """Trouve l'année dispo la plus proche (favorise la plus récente si égalité)."""
    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT DISTINCT annee FROM {schema}.{table} ORDER BY annee")
        )
        annees = [row[0] for row in result]

    if not annees:
        return None
    if annee_cible in annees:
        return annee_cible

    # plus proche, en cas d'égalité on prend la plus récente
    return max(annees, key=lambda a: (-abs(a - annee_cible), a))


def _fetch_logements(engine, annee):
    annee_eff = _resolve_annee(engine, "indicateurs_logements_sociaux_iris", "gold", annee)
    if annee_eff is None:
        return pd.DataFrame(columns=["code_iris", "nb_logements_sociaux_finances"])

    query = text("""
        SELECT code_iris, nb_logements_sociaux_finances
        FROM gold.indicateurs_logements_sociaux_iris
        WHERE annee = :annee
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"annee": annee_eff})


def _fetch_socio_eco(engine, annee):
    annee_eff = _resolve_annee(engine, "indicateurs_socio_eco_iris", "gold", annee)
    if annee_eff is None:
        return pd.DataFrame(columns=["code_iris", "revenu_median", "prix_m2_median", "iai"])

    query = text("""
        SELECT code_iris, revenu_median, prix_m2_median, iai
        FROM gold.indicateurs_socio_eco_iris
        WHERE annee = :annee
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"annee": annee_eff})


def _fetch_environnement(engine):
    query = text("SELECT code_iris, score FROM gold.score_environnemental")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.rename(columns={"score": "score_environnemental"})


def _fetch_reseau(engine):
    query = text("""
        SELECT code_iris, score_final, meilleur_operateur_mobile, meilleur_operateur_fibre
        FROM gold.score_reseau
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.rename(columns={"score_final": "score_reseau"})


def _build_iris_dataframe(annee: int) -> pd.DataFrame:
    engine = get_engine()
    ref = _get_iris_referentiel()

    logements = _fetch_logements(engine, annee)
    socio = _fetch_socio_eco(engine, annee)
    enviro = _fetch_environnement(engine)
    reseau = _fetch_reseau(engine)

    # left join tout sur le référentiel
    df = ref.merge(logements, on="code_iris", how="left")
    df = df.merge(socio, on="code_iris", how="left")
    df = df.merge(enviro, on="code_iris", how="left")
    df = df.merge(reseau, on="code_iris", how="left")

    df["nb_logements_sociaux_finances"] = df["nb_logements_sociaux_finances"].fillna(0).astype(int)

    return df


def get_indicateurs_iris(annee: int = 2025) -> list[dict]:
    df = _build_iris_dataframe(annee)
    return _sanitize(df.to_dict(orient="records"))


def get_indicateurs_arrondissement(annee: int = 2025) -> list[dict]:
    df = _build_iris_dataframe(annee)

    numeric_cols = [
        "nb_logements_sociaux_finances", "revenu_median",
        "prix_m2_median", "iai", "score_environnemental", "score_reseau",
    ]
    text_cols = ["meilleur_operateur_mobile", "meilleur_operateur_fibre"]

    # agrégation : sum pour logements, mean pour les autres, mode pour les opérateurs
    agg_dict = {"nb_logements_sociaux_finances": "sum"}
    for col in ["revenu_median", "prix_m2_median", "iai", "score_environnemental", "score_reseau"]:
        agg_dict[col] = "mean"

    grouped = df.groupby("arrondissement")
    result = grouped.agg(agg_dict).reset_index()

    # mode pour les opérateurs (le plus fréquent par arrondissement)
    for col in text_cols:
        modes = grouped[col].agg(lambda x: x.dropna().mode().iloc[0] if not x.dropna().empty else None)
        result = result.merge(modes.rename(col), on="arrondissement", how="left", suffixes=("_drop", ""))
        if f"{col}_drop" in result.columns:
            result = result.drop(columns=[f"{col}_drop"])

    return _sanitize(result.to_dict(orient="records"))
