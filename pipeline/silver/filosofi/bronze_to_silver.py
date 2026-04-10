import sys
import re
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
from config import DATA_RAW
from db import engine

FILOSOFI_DIR = DATA_RAW / "filosofi"


def trouver_fichiers():
    """Trouve les CSV Filosofi et extrait l'année depuis le nom de fichier."""
    fichiers = {}
    for csv_path in sorted(FILOSOFI_DIR.glob("*.csv")):
        # le nom contient l'année : BASE_TD_FILO_..._2021_DISP.csv ou BASE_TD_FILO_DISP_..._2020.csv
        match = re.search(r"(20\d{2})", csv_path.name)
        if match:
            annee = int(match.group(1))
            fichiers[annee] = csv_path
    return fichiers


def lire_et_nettoyer(csv_path, annee):
    # la colonne du revenu médian change selon l'année : DISP_MED21, DISP_MED20, etc.
    suffixe = str(annee)[-2:]
    col_median = f"DISP_MED{suffixe}"

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8", dtype=str)

    if col_median not in df.columns:
        print(f"  colonne {col_median} introuvable dans {csv_path.name}")
        print(f"  colonnes disponibles : {[c for c in df.columns if 'MED' in c]}")
        return pd.DataFrame()

    # on ne garde que les colonnes utiles
    df = df[["IRIS", col_median]].copy()
    df = df.rename(columns={"IRIS": "code_iris", col_median: "revenu_median"})

    # on filtre sur Paris (code IRIS commence par 751)
    df = df[df["code_iris"].str.startswith("751")].copy()

    # les valeurs "ns" (secret stat) et "nd" (non dispo) deviennent NULL
    # certains millésimes utilisent la virgule comme séparateur décimal
    df["revenu_median"] = df["revenu_median"].str.replace(",", ".", regex=False)
    df["revenu_median"] = pd.to_numeric(df["revenu_median"], errors="coerce")

    df["annee"] = annee

    # on extrait l'arrondissement depuis le code IRIS
    # code IRIS Paris = 751AAIIII où AA = arrondissement (01 à 20)
    df["arrondissement"] = df["code_iris"].str[3:5].astype(int)

    sans_revenu = df["revenu_median"].isna().sum()
    if sans_revenu > 0:
        print(f"  {sans_revenu} IRIS sans revenu médian (secret stat ou non dispo)")

    print(f"  {annee} : {len(df)} IRIS Paris, {df['revenu_median'].notna().sum()} avec revenu médian")
    return df


def filtrer_nouvelles_lignes(df):
    existants = pd.read_sql(
        "SELECT code_iris, annee FROM silver.filosofi",
        engine,
    )
    # on merge pour trouver les lignes déjà en base
    merged = df.merge(existants, on=["code_iris", "annee"], how="left", indicator=True)
    df_nouvelles = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])

    nb_skip = len(df) - len(df_nouvelles)
    if nb_skip > 0:
        print(f"  {nb_skip} lignes déjà en base — ignorées")
    return df_nouvelles


def inserer_silver(df):
    colonnes_table = ["code_iris", "annee", "revenu_median", "arrondissement"]
    df = df[colonnes_table]

    df.to_sql(
        "filosofi",
        engine,
        schema="silver",
        if_exists="append",
        index=False,
    )
    print(f"silver.filosofi : {len(df)} nouvelles lignes insérées")


def run():
    fichiers = trouver_fichiers()

    if not fichiers:
        print("aucun fichier Filosofi trouvé — lancer d'abord : python download_filosofi.py")
        return

    print(f"{len(fichiers)} fichiers Filosofi trouvés : {sorted(fichiers.keys())}")

    tous_les_df = []
    for annee, csv_path in sorted(fichiers.items()):
        df = lire_et_nettoyer(csv_path, annee)
        if len(df) > 0:
            tous_les_df.append(df)

    if not tous_les_df:
        return

    df_total = pd.concat(tous_les_df, ignore_index=True)
    df_total = filtrer_nouvelles_lignes(df_total)

    if len(df_total) == 0:
        print("aucune nouvelle ligne à insérer")
        return

    inserer_silver(df_total)


if __name__ == "__main__":
    run()
