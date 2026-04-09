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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRONZE_DIR = os.path.join(BASE_DIR, "Data", "Bronze")

PATHS = {
    "nb_classes": os.path.join(BRONZE_DIR, "Etablissements_scolaire", "fr-en-ecoles-effectifs-nb_classes.csv"),
    "colleges": os.path.join(BRONZE_DIR, "Etablissements_scolaire", "etablissements-scolaires-colleges.csv"),
    "elementaires": os.path.join(BRONZE_DIR, "Etablissements_scolaire", "etablissements-scolaires-ecoles-elementaires.csv"),
    "maternelles": os.path.join(BRONZE_DIR, "Etablissements_scolaire", "etablissements-scolaires-maternelles.csv"),
    "age_insee": os.path.join(BRONZE_DIR, "Population", "age-insee-2020.xlsx"),
    "population": os.path.join(BRONZE_DIR, "Population", "population_paris_2026.csv"),
    "bpe_sante": os.path.join(BRONZE_DIR, "Sante", "BPE_SANTE_ACTION_SOCIALE_FR.xlsx"),
    "hopitaux": os.path.join(BRONZE_DIR, "Sante", "les_etablissements_hospitaliers_franciliens.csv"),
}
