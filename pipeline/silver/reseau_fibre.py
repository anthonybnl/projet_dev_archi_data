import json
import warnings
from datetime import datetime

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, Point

from pipeline.config import PATHS, LAYERS
from pipeline.db import insert_if_empty

warnings.filterwarnings("ignore")

# Opérateur d'infrastructure identifié via la colonne ARCEP code_l331
OPERATEUR_L331 = {
    "FRTE": "Orange",
    "SFR0": "SFR",
    "FREE": "Free",
    "NURC": "Bouygues",
}


def load_iris() -> gpd.GeoDataFrame:
    with open(PATHS["iris_geojson"], encoding="utf-8") as f:
        geojson = json.load(f)

    rows = []
    for feat in geojson["features"]:
        props = feat["properties"]
        if props.get("dep") != "75":
            continue
        insee_com = int(props["insee_com"])
        rows.append({
            "code_iris": props["code_iris"],
            "arrondissement": insee_com - 75100,
            "geometry": shape(feat["geometry"]),
        })

    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    return gdf.to_crs("EPSG:2154")


def load_paris_fibre() -> pd.DataFrame:
    """
    Lecture par chunks de 100k lignes.
    On filtre Paris via code_poste (750XX) en ne chargeant que les colonnes utiles.
    """
    frames = []
    chunks = pd.read_csv(
        PATHS["fibre"],
        sep=",",
        chunksize=100_000,
        low_memory=False,
        usecols=["x", "y", "code_poste", "imb_etat", "pm_etat", "code_l331"],
    )
    for chunk in chunks:
        paris = chunk[chunk["code_poste"].astype(str).str.match(r"^750\d\d$")].copy()
        if len(paris):
            frames.append(paris)

    df = pd.concat(frames, ignore_index=True)
    df["operateur"] = df["code_l331"].map(OPERATEUR_L331).fillna(df["code_l331"])
    df["arrondissement"] = df["code_poste"].astype(int) - 75000
    return df


def sjoin_iris(df: pd.DataFrame, iris_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Spatial join : associe chaque immeuble (x, y) à son IRIS.
    Les coordonnées x et y du fichier ARCEP.
    """
    # Suppression des lignes sans coordonnées valides
    df = df.dropna(subset=["x", "y"]).copy()
    df["x"] = pd.to_numeric(df["x"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df = df.dropna(subset=["x", "y"])

    # Les colonnes x et y du fichier ARCEP sont en (lon, lat)
    gdf_imb = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["x"], df["y"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2154")

    # sjoin : chaque immeuble récupère le code_iris de son IRIS
    joined = gpd.sjoin(
        gdf_imb,
        iris_gdf[["code_iris", "arrondissement", "geometry"]],
        how="left",
        predicate="within",
    )
    return joined


def run(engine):
    print("[silver.reseau_fibre] Chargement contours IRIS Paris...")
    iris = load_iris()
    print(f"[silver.reseau_fibre] {len(iris)} IRIS charges")

    print("[silver.reseau_fibre] Chargement donnees fibre Paris (lecture par chunks)...")
    df = load_paris_fibre()
    print(f"[silver.reseau_fibre] {len(df)} immeubles Paris charges")

    print("[silver.reseau_fibre] Association IRIS par coordonnees (sjoin)...")
    joined = sjoin_iris(df, iris)

    # Immeubles sans IRIS trouvé (coordonnées manquantes), on ignore
    joined = joined.dropna(subset=["code_iris"])
    joined["arrondissement"] = joined["arrondissement_right"].fillna(
        joined["arrondissement_left"]
    ).astype(int)

    # Taux de déploiement par IRIS
    total = joined.groupby("code_iris").size().rename("total_imb")
    deploye = (
        joined[joined["imb_etat"] == "deploye"]
        .groupby("code_iris").size()
        .rename("imb_deployes")
    )
    pm_actif = (
        joined[joined["pm_etat"] == "deploye"]
        .groupby("code_iris").size()
        .rename("pm_actifs")
    )

    result = pd.concat([total, deploye, pm_actif], axis=1).fillna(0).reset_index()
    result["imb_deployes"] = result["imb_deployes"].astype(int)
    result["pm_actifs"] = result["pm_actifs"].astype(int)
    result["taux_deploiement"] = (result["imb_deployes"] / result["total_imb"] * 100).round(2)
    result["taux_pm_actif"] = (result["pm_actifs"] / result["total_imb"] * 100).round(2)

    # Meilleur opérateur fibre par IRIS
    # plus grand nombre d'immeubles avec imb ET PM tous les deux déployés
    operationnel = joined[(joined["imb_etat"] == "deploye") & (joined["pm_etat"] == "deploye")]
    counts = (
        operationnel.groupby(["code_iris", "operateur"])
        .size()
        .reset_index(name="nb_imb_operationnel")
    )
    if len(counts):
        idx = counts.groupby("code_iris")["nb_imb_operationnel"].idxmax()
        meilleur = counts.loc[idx, ["code_iris", "operateur"]].rename(
            columns={"operateur": "meilleur_operateur_fibre"}
        )
        result = result.merge(meilleur, on="code_iris", how="left")
    else:
        result["meilleur_operateur_fibre"] = None

    # Score_Fibre = 0.60 * taux_deploiement + 0.40 * taux_pm_actif
    result["score_fibre"] = (
            0.60 * result["taux_deploiement"]
            + 0.40 * result["taux_pm_actif"]
    ).round(2)

    # Récupération de l'arrondissement depuis le sjoin
    arrd_map = joined[["code_iris", "arrondissement"]].drop_duplicates("code_iris")
    result = result.merge(arrd_map, on="code_iris", how="left")
    result["arrondissement"] = result["arrondissement"].fillna(0).astype(int)

    result["created_at"] = datetime.now()

    schema = LAYERS["silver_schema"]
    inserted = insert_if_empty(result, "reseau_fibre", engine, schema)
    if inserted:
        print(f"[silver.reseau_fibre] {len(result)} IRIS inseres")
    else:
        print("[silver.reseau_fibre] table deja remplie, aucune insertion")
