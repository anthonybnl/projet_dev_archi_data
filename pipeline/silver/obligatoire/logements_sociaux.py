import sys
from pathlib import Path

# on ajoute le dossier pipeline/ pour pouvoir importer config et db
sys.path.append(str(Path(__file__).parent.parent.parent))

import requests as req
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

root_path = Path(__file__).resolve().parents[3]
if not str(root_path) in sys.path:
    sys.path.insert(0, str(root_path))

from pipeline.config import IRIS_PATH, PATHS
from pipeline.db import get_engine

if not IRIS_PATH.exists():
    raise FileNotFoundError(f"fichier IRIS introuvable ({IRIS_PATH})")

CSV_PATH = PATHS["logements_sociaux"]

# mapping des colonnes brutes vers des noms propres en snake_case
RENAME_COLS = {
    "Identifiant livraison": "identifiant_livraison",
    "Adresse du programme": "adresse",
    "Code postal": "code_postal",
    "Ville": "ville",
    "Année du financement - agrément": "annee_financement",
    "Bailleur social": "bailleur_social",
    "Nombre total de logements financés": "nb_logements_finances",
    "Dont nombre de logements PLA I": "nb_plai",
    "Dont nombre de logements PLUS": "nb_plus",
    "Dont nombre de logements PLUS CD": "nb_plus_cd",
    "Dont nombre de logements PLS": "nb_pls",
    "Mode de réalisation": "mode_realisation",
    "Commentaires": "commentaires",
    "Arrondissement": "arrondissement",
    "Nature de programme": "nature_programme",
    "Coordonnée en X (L93)": "x_l93",
    "Coordonnée en Y (L93)": "y_l93",
    "geo_shape": "geo_shape",
    "geo_point_2d": "geo_point_2d",
}


def lire_et_nettoyer_csv():
    # utf-8-sig pour gérer le BOM que Windows ajoute souvent aux CSV
    df = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8-sig")
    df = df.rename(columns=RENAME_COLS)

    # on parse geo_point_2d ("lat, lon") en deux colonnes float
    coords = df["geo_point_2d"].str.split(", ", expand=True)
    df["latitude"] = pd.to_numeric(coords[0], errors="coerce")
    df["longitude"] = pd.to_numeric(coords[1], errors="coerce")
    df = df.drop(columns=["geo_point_2d", "geo_shape"])

    # on cast les colonnes numériques en Int64 (nullable) pour ne pas planter sur les NaN
    cols_int = [
        "annee_financement", "nb_logements_finances",
        "nb_plai", "nb_plus", "nb_plus_cd", "nb_pls", "arrondissement",
    ]
    for col in cols_int:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df["x_l93"] = pd.to_numeric(df["x_l93"], errors="coerce")
    df["y_l93"] = pd.to_numeric(df["y_l93"], errors="coerce")

    # on force identifiant_livraison en string pour la PK
    df["identifiant_livraison"] = df["identifiant_livraison"].astype(str)

    print(f"CSV lu et nettoyé : {len(df)} lignes")
    return df


def telecharger_iris():
    """Télécharge le fichier IRIS une seule fois."""
    if IRIS_PATH.exists():
        print(f"fichier IRIS déjà présent : {IRIS_PATH.name}")
        return
    print("téléchargement des contours IRIS depuis data.gouv.fr...")
    response = req.get(IRIS_URL, stream=True)
    response.raise_for_status()
    IRIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(IRIS_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("fichier IRIS téléchargé")


def charger_iris_paris():
    gdf = gpd.read_file(IRIS_PATH)

    # on cherche la colonne du code commune pour filtrer sur Paris (751xx)
    # selon la version du fichier elle peut être en majuscules ou minuscules
    col_commune = None
    for candidat in ["INSEE_COM", "insee_com", "depcom", "code_commune"]:
        if candidat in gdf.columns:
            col_commune = candidat
            break

    if col_commune is None:
        raise ValueError(f"impossible de trouver la colonne commune. Colonnes : {list(gdf.columns)}")

    # on force en string parce que dans certaines versions insee_com est un int (75101)
    gdf[col_commune] = gdf[col_commune].astype(str)
    gdf_paris = gdf[gdf[col_commune].str.startswith("751")].copy()
    print(f"IRIS Paris : {len(gdf_paris)} zones chargées")

    # on identifie la colonne du code IRIS complet (9 caractères)
    col_code_iris = None
    for candidat in ["CODE_IRIS", "code_iris", "iris_code"]:
        if candidat in gdf_paris.columns:
            col_code_iris = candidat
            break
    if col_code_iris is None:
        col_code_iris = [c for c in gdf_paris.columns if "iris" in c.lower() and gdf_paris[c].dtype == "object"][0]

    gdf_paris = gdf_paris[[col_code_iris, "geometry"]].rename(columns={col_code_iris: "code_iris"})

    # on s'assure d'être en WGS84 pour matcher avec nos coordonnées GPS
    if gdf_paris.crs and gdf_paris.crs.to_epsg() != 4326:
        gdf_paris = gdf_paris.to_crs(epsg=4326)

    return gdf_paris


def enrichir_iris(df):
    """Ajoute la colonne code_iris via jointure spatiale point-in-polygon."""
    telecharger_iris()
    gdf_iris = charger_iris_paris()

    mask_coords = df["latitude"].notna() & df["longitude"].notna()
    df_avec = df[mask_coords].copy()
    df_sans = df[~mask_coords].copy()

    if len(df_sans) > 0:
        print(f"  {len(df_sans)} lignes sans coordonnées — code_iris restera NULL")

    geometry = [Point(lon, lat) for lon, lat in zip(df_avec["longitude"], df_avec["latitude"])]
    gdf_logements = gpd.GeoDataFrame(df_avec, geometry=geometry, crs="EPSG:4326")

    gdf_enrichi = gpd.sjoin(gdf_logements, gdf_iris, how="left", predicate="within")

    # on gère les doublons en cas de frontière IRIS
    gdf_enrichi = gdf_enrichi.drop_duplicates(subset=["identifiant_livraison"], keep="first")
    gdf_enrichi = gdf_enrichi.drop(columns=["index_right", "geometry"], errors="ignore")

    # on recolle les lignes sans coordonnées
    df_sans["code_iris"] = None
    df_resultat = pd.concat([gdf_enrichi, df_sans], ignore_index=True)

    nb_enrichis = df_resultat["code_iris"].notna().sum()
    print(f"  {nb_enrichis}/{len(df_resultat)} lignes enrichies avec un code IRIS")
    return df_resultat


def filtrer_nouvelles_lignes(engine, df):
    """Ne garde que les lignes dont l'identifiant_livraison n'est pas déjà en base."""
    ids_existants = pd.read_sql(
        "SELECT identifiant_livraison FROM silver.logements_sociaux",
        engine,
    )["identifiant_livraison"].tolist()

    df_nouvelles = df[~df["identifiant_livraison"].isin(ids_existants)]
    nb_skip = len(df) - len(df_nouvelles)
    if nb_skip > 0:
        print(f"  {nb_skip} lignes déjà en base — ignorées")
    return df_nouvelles


def inserer_silver(engine, df):
    # on s'assure que les colonnes sont dans le bon ordre et qu'on n'envoie que ce que la table attend
    colonnes_table = [
        "identifiant_livraison", "adresse", "code_postal", "ville",
        "annee_financement", "bailleur_social", "nb_logements_finances",
        "nb_plai", "nb_plus", "nb_plus_cd", "nb_pls",
        "mode_realisation", "commentaires", "arrondissement", "nature_programme",
        "x_l93", "y_l93", "latitude", "longitude", "code_iris",
    ]
    df = df[colonnes_table]

    df.to_sql(
        "logements_sociaux",
        engine,
        schema="silver",
        if_exists="append",
        index=False,
    )
    print(f"silver.logements_sociaux : {len(df)} nouvelles lignes insérées")


def run():
    engine = get_engine()
    df = lire_et_nettoyer_csv()
    df = enrichir_iris(df)
    df = filtrer_nouvelles_lignes(engine, df)

    if len(df) == 0:
        print("aucune nouvelle ligne à insérer")
        return

    inserer_silver(engine, df)


if __name__ == "__main__":
    run()
