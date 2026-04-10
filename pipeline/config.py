import os
import yaml


def load_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()
DB = CONFIG["database"]
LAYERS = CONFIG["layers"]

# Paths
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")

PATHS = {
    "nb_classes": os.path.join(RAW_DIR, "Etablissements_scolaire", "fr-en-ecoles-effectifs-nb_classes.csv"),
    "colleges": os.path.join(RAW_DIR, "Etablissements_scolaire", "etablissements-scolaires-colleges.csv"),
    "elementaires": os.path.join(RAW_DIR, "Etablissements_scolaire", "etablissements-scolaires-ecoles-elementaires.csv"),
    "maternelles": os.path.join(RAW_DIR, "Etablissements_scolaire", "etablissements-scolaires-maternelles.csv"),
    "age_insee": os.path.join(RAW_DIR, "Population", "age-insee-2020.xlsx"),
    "population": os.path.join(RAW_DIR, "Population", "population_paris_2026.csv"),
    "bpe_sante": os.path.join(RAW_DIR, "Sante", "BPE_SANTE_ACTION_SOCIALE_FR.xlsx"),
    "hopitaux": os.path.join(RAW_DIR, "Sante", "les_etablissements_hospitaliers_franciliens.csv"),

    # Réseau mobile
    "antennes": os.path.join(RAW_DIR, "reseau", "antennes-relais.csv"),
    "couverture_dir": os.path.join(RAW_DIR, "reseau", "couverture_theorique"),
    "qos_habitations": os.path.join(RAW_DIR, "reseau", "2025_QoS_Metropole_data_habitations.csv"),

    # Réseau fibre
    "fibre": os.path.join(RAW_DIR, "reseau", "carte_fibre_immeubles_2025_T4_20260130.csv"),

    # GeoJSON arrondissements (front)
    "arrondissements_geojson": os.path.join(BASE_DIR, "front", "src", "assets", "arrondissements.geojson"),

    # GeoJSON IRIS Paris (granularité fine, environ 992 zones)
    "iris_geojson": os.path.join(RAW_DIR, "map", "iris.geojson"),
}
