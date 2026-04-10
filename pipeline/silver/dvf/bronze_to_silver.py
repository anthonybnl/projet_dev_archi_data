import sys
import hashlib
import time
import io
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import requests as req
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from config import DATA_RAW, DATA_REFERENTIELS
from db import engine

# on liste tous les fichiers DVF (.txt et .csv, même format séparateur |)
DVF_FILES = sorted(DATA_RAW.glob("ValeursFoncieres-*"))

# même fichier IRIS que le pipeline logements sociaux, déjà téléchargé normalement
IRIS_PATH = DATA_REFERENTIELS / "contours-iris-france.geojson"

# API Géoplateforme (remplace l'ancienne api-adresse.data.gouv.fr)
GEOCODE_URL = "https://data.geopf.fr/geocodage/search/csv"
# on découpe en chunks pour ne pas dépasser 50 Mo / 200k lignes
GEOCODE_CHUNK_SIZE = 5000
# pause entre chaque batch pour ne pas taper la limite de 50 req/s
GEOCODE_PAUSE = 1.5
# nombre de tentatives en cas de 429
GEOCODE_MAX_RETRIES = 5

RENAME_COLS = {
    "No disposition": "no_disposition",
    "Date mutation": "date_mutation",
    "Nature mutation": "nature_mutation",
    "Valeur fonciere": "valeur_fonciere",
    "No voie": "no_voie",
    "Type de voie": "type_voie",
    "Voie": "voie",
    "Code postal": "code_postal",
    "Commune": "commune",
    "Code departement": "code_departement",
    "Code commune": "code_commune",
    "Section": "section",
    "No plan": "no_plan",
    "Code type local": "code_type_local",
    "Type local": "type_local",
    "Surface reelle bati": "surface_reelle_bati",
    "Nombre pieces principales": "nombre_pieces",
    "Surface terrain": "surface_terrain",
}


def generer_id_mutation(row):
    """On génère un ID déterministe à partir des colonnes clés de la ligne.
    Comme ça, si on relance le pipeline, le même enregistrement produit le même ID."""
    cle = "|".join(str(row.get(c, "")) for c in [
        "date_mutation", "no_disposition", "code_commune",
        "section", "no_plan", "no_voie", "voie",
        "code_type_local", "surface_reelle_bati", "nombre_pieces",
    ])
    return hashlib.md5(cle.encode()).hexdigest()


def lire_dvf_paris(fichier):
    """Lit un fichier DVF, ne garde que Paris et les Appartements/Maisons."""
    df = pd.read_csv(
        fichier,
        sep="|",
        encoding="utf-8",
        low_memory=False,
        usecols=list(RENAME_COLS.keys()),
        dtype=str,
    )
    df = df.rename(columns=RENAME_COLS)

    # on filtre sur Paris (département 75)
    df = df[df["code_departement"] == "75"].copy()

    # on ne garde que les Appartements (2) et Maisons (1) — pas les dépendances ni terrains
    df = df[df["code_type_local"].isin(["1", "2"])].copy()

    return df


def nettoyer_dvf(df):
    # valeur foncière : format français "1042000,00" → float
    df["valeur_fonciere"] = (
        df["valeur_fonciere"]
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

    df["date_mutation"] = pd.to_datetime(df["date_mutation"], format="%d/%m/%Y", errors="coerce")

    for col in ["surface_reelle_bati", "nombre_pieces", "surface_terrain"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # on calcule l'arrondissement depuis le code commune (120 → 20e)
    df["arrondissement"] = pd.to_numeric(df["code_commune"], errors="coerce").astype("Int64")

    # on génère l'id déterministe
    df["id_mutation"] = df.apply(generer_id_mutation, axis=1)

    # on déduplique sur l'id — les vrais doublons DVF (lots multiples) sont éliminés
    avant = len(df)
    df = df.drop_duplicates(subset=["id_mutation"], keep="first")
    dupes = avant - len(df)
    if dupes > 0:
        print(f"  {dupes} doublons supprimés")

    # on supprime les colonnes intermédiaires
    df = df.drop(columns=["code_type_local", "no_disposition"], errors="ignore")

    return df


def geocoder_batch(df):
    """Géocode les adresses via l'API Géoplateforme en envoyant des CSV par batch."""
    # on construit l'adresse complète pour le géocodage
    df["adresse_complete"] = (
        df["no_voie"].fillna("") + " " +
        df["type_voie"].fillna("") + " " +
        df["voie"].fillna("")
    ).str.strip()

    # on prépare un df avec juste ce qu'il faut pour l'API
    df_geo = df[["id_mutation", "adresse_complete", "code_postal"]].copy()
    df_geo = df_geo.rename(columns={"adresse_complete": "adresse", "code_postal": "postcode"})

    # on ne géocode que les lignes qui ont une adresse
    mask_adresse = df_geo["adresse"].str.len() > 2
    df_a_geocoder = df_geo[mask_adresse].copy()
    print(f"  {len(df_a_geocoder)} adresses à géocoder ({len(df_geo) - len(df_a_geocoder)} sans adresse)")

    resultats = []
    nb_chunks = (len(df_a_geocoder) // GEOCODE_CHUNK_SIZE) + 1

    for i in range(0, len(df_a_geocoder), GEOCODE_CHUNK_SIZE):
        chunk = df_a_geocoder.iloc[i:i + GEOCODE_CHUNK_SIZE]
        chunk_num = (i // GEOCODE_CHUNK_SIZE) + 1

        csv_buffer = io.StringIO()
        chunk.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        # on retry en cas de 429 (rate limit)
        for tentative in range(GEOCODE_MAX_RETRIES):
            response = req.post(
                GEOCODE_URL,
                files={"data": ("batch.csv", csv_bytes, "text/csv")},
                data={
                    "columns": "adresse",
                    "postcode": "postcode",
                },
                timeout=120,
            )

            if response.status_code == 200:
                break
            elif response.status_code == 429:
                # l'API nous demande d'attendre
                attente = int(response.headers.get("retry-after", 5))
                print(f"  rate limit atteint, on attend {attente}s (tentative {tentative + 1}/{GEOCODE_MAX_RETRIES})")
                time.sleep(attente)
            else:
                print(f"  erreur API géocodage : {response.status_code}")
                break
        else:
            print(f"  chunk {chunk_num} abandonné après {GEOCODE_MAX_RETRIES} tentatives")
            continue

        if response.status_code == 200:
            df_result = pd.read_csv(io.StringIO(response.text))
            resultats.append(df_result)
            print(f"  chunk {chunk_num}/{nb_chunks} géocodé ({len(chunk)} adresses)")

        # on attend un peu entre chaque batch pour ne pas saturer
        if i + GEOCODE_CHUNK_SIZE < len(df_a_geocoder):
            time.sleep(GEOCODE_PAUSE)

    if not resultats:
        print("  aucun résultat de géocodage")
        df["latitude"] = None
        df["longitude"] = None
        return df

    df_geocode = pd.concat(resultats, ignore_index=True)

    # l'API renvoie les colonnes result_latitude et result_longitude
    col_lat = "result_latitude" if "result_latitude" in df_geocode.columns else "latitude"
    col_lon = "result_longitude" if "result_longitude" in df_geocode.columns else "longitude"

    df_geocode = df_geocode[["id_mutation", col_lat, col_lon]].rename(
        columns={col_lat: "latitude", col_lon: "longitude"}
    )

    # on merge les coordonnées sur le df principal
    df = df.drop(columns=["latitude", "longitude"], errors="ignore")
    df = df.merge(df_geocode, on="id_mutation", how="left")

    nb_geocode = df["latitude"].notna().sum()
    print(f"  {nb_geocode}/{len(df)} lignes géocodées")

    # on supprime la colonne temporaire
    df = df.drop(columns=["adresse_complete"], errors="ignore")

    return df


def enrichir_iris(df):
    """Jointure spatiale point-in-polygon pour ajouter le code IRIS."""
    if not IRIS_PATH.exists():
        print(f"  fichier IRIS introuvable ({IRIS_PATH.name}) — lancer d'abord le pipeline logements sociaux")
        df["code_iris"] = None
        return df

    gdf_iris = gpd.read_file(IRIS_PATH)

    # même logique que logements sociaux : on cherche la colonne commune et on filtre Paris
    col_commune = None
    for candidat in ["INSEE_COM", "insee_com", "depcom", "code_commune"]:
        if candidat in gdf_iris.columns:
            col_commune = candidat
            break
    if col_commune is None:
        raise ValueError(f"colonne commune introuvable dans IRIS. Colonnes : {list(gdf_iris.columns)}")

    gdf_iris[col_commune] = gdf_iris[col_commune].astype(str)
    gdf_iris = gdf_iris[gdf_iris[col_commune].str.startswith("751")].copy()

    col_code_iris = None
    for candidat in ["CODE_IRIS", "code_iris"]:
        if candidat in gdf_iris.columns:
            col_code_iris = candidat
            break
    if col_code_iris is None:
        col_code_iris = [c for c in gdf_iris.columns if "iris" in c.lower() and gdf_iris[c].dtype == "object"][0]

    gdf_iris = gdf_iris[[col_code_iris, "geometry"]].rename(columns={col_code_iris: "code_iris"})

    if gdf_iris.crs and gdf_iris.crs.to_epsg() != 4326:
        gdf_iris = gdf_iris.to_crs(epsg=4326)

    # on sépare les lignes avec et sans coordonnées
    mask = df["latitude"].notna() & df["longitude"].notna()
    df_avec = df[mask].copy()
    df_sans = df[~mask].copy()

    if len(df_sans) > 0:
        print(f"  {len(df_sans)} lignes sans coordonnées — code_iris restera NULL")

    geometry = [Point(lon, lat) for lon, lat in zip(df_avec["longitude"], df_avec["latitude"])]
    gdf = gpd.GeoDataFrame(df_avec, geometry=geometry, crs="EPSG:4326")

    gdf_enrichi = gpd.sjoin(gdf, gdf_iris, how="left", predicate="within")
    gdf_enrichi = gdf_enrichi.drop_duplicates(subset=["id_mutation"], keep="first")
    gdf_enrichi = gdf_enrichi.drop(columns=["index_right", "geometry"], errors="ignore")

    df_sans["code_iris"] = None
    df_resultat = pd.concat([gdf_enrichi, df_sans], ignore_index=True)

    nb = df_resultat["code_iris"].notna().sum()
    print(f"  {nb}/{len(df_resultat)} lignes enrichies avec un code IRIS")
    return df_resultat


def filtrer_nouvelles_lignes(df):
    """Ne garde que les lignes dont l'id_mutation n'est pas déjà en base."""
    ids_existants = pd.read_sql(
        "SELECT id_mutation FROM silver.dvf",
        engine,
    )["id_mutation"].tolist()

    df_nouvelles = df[~df["id_mutation"].isin(ids_existants)]
    nb_skip = len(df) - len(df_nouvelles)
    if nb_skip > 0:
        print(f"  {nb_skip} lignes déjà en base — ignorées")
    return df_nouvelles


def inserer_silver(df):
    colonnes_table = [
        "id_mutation", "date_mutation", "nature_mutation", "valeur_fonciere",
        "no_voie", "type_voie", "voie", "code_postal", "commune",
        "code_departement", "code_commune", "arrondissement",
        "section", "no_plan", "type_local",
        "surface_reelle_bati", "nombre_pieces", "surface_terrain",
        "latitude", "longitude", "code_iris",
    ]
    df = df[colonnes_table]

    df.to_sql(
        "dvf",
        engine,
        schema="silver",
        if_exists="append",
        index=False,
    )
    print(f"silver.dvf : {len(df)} nouvelles lignes insérées")


def run():
    if not DVF_FILES:
        print("aucun fichier DVF trouvé dans data/raw/")
        return

    print(f"{len(DVF_FILES)} fichiers DVF trouvés")

    for fichier in DVF_FILES:
        print(f"\n--- {fichier.name} ---")

        df = lire_dvf_paris(fichier)
        print(f"  {len(df)} lignes Paris (Appartements + Maisons)")

        if len(df) == 0:
            continue

        df = nettoyer_dvf(df)
        df = filtrer_nouvelles_lignes(df)

        if len(df) == 0:
            print("  aucune nouvelle ligne à insérer")
            continue

        df = geocoder_batch(df)
        df = enrichir_iris(df)
        inserer_silver(df)


if __name__ == "__main__":
    run()
