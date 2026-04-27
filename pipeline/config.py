import os
from pathlib import Path

# Paths
BASE_DIR   = Path(__file__).resolve().parents[1]

print(f"BASE_DIR: {BASE_DIR}")

DATA_DIR   = BASE_DIR / "data"

RAW_DIR    = DATA_DIR / "raw"
IRIS_PATH = RAW_DIR / "map" / "iris.geojson"

PATHS = {
    "nb_classes": str(RAW_DIR / "AES" / "fr-en-ecoles-effectifs-nb_classes.csv"),
    "colleges": str(RAW_DIR / "AES" / "etablissements-scolaires-colleges.csv"),
    "elementaires": str(RAW_DIR / "AES" / "etablissements-scolaires-ecoles-elementaires.csv"),
    "maternelles": str(RAW_DIR / "AES" / "etablissements-scolaires-maternelles.csv"),
    "age_insee": str(RAW_DIR / "AES" / "age-insee-2020.xlsx"),
    "population": str(RAW_DIR / "AES" / "population_paris_2026.csv"),
    "bpe_sante": str(RAW_DIR / "AES" / "BPE_SANTE_ACTION_SOCIALE_FR.xlsx"),
    "hopitaux": str(RAW_DIR / "AES" / "les_etablissements_hospitaliers_franciliens.csv"),

    # Réseau mobile
    "antennes": str(RAW_DIR / "reseau" / "antennes-relais.csv"),
    "couverture_dir": str(RAW_DIR / "reseau" / "couverture_theorique"),
    "qos_habitations": str(RAW_DIR / "reseau" / "2025_QoS_Metropole_data_habitations.csv"),

    # Réseau fibre
    "fibre": str(RAW_DIR / "reseau" / "carte_fibre_immeubles_2025_T4_20260130.csv"),

    # GeoJSON arrondissements (front)
    "arrondissements_geojson": str(BASE_DIR / "front" / "src" / "assets" / "arrondissements.geojson"),

    # GeoJSON IRIS Paris (granularité fine, environ 992 zones)
    "iris_geojson": str(RAW_DIR / "map" / "iris.geojson"),

    # logements sociaux
    "logements_sociaux": str(RAW_DIR / "obligatoire" / "logements-sociaux-finances-a-paris.csv"),
}
 
