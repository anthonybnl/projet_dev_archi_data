import os
from dotenv import load_dotenv
import py7zr
import geopandas as gpd
from shapely.geometry import box
from download import function_unzip, download_file, download_from_index


load_dotenv(dotenv_path="url.env")

URLS_CONFIG = {
    "reseau": {
        "debit_fibre": os.getenv("ENV_HAUT_DEBIT_FIBRE_URL"),
        "antenne_reseau": os.getenv("ENV_ANTENNE_RESEAU_URL"),
        "couverture_theorique": os.getenv("ENV_CONVERTURES_THEORIQUE_URL")
    }
}

for key, value in URLS_CONFIG.items():
    for v in value.values():
        url = v
        path = download_file(url)
        function_unzip(path)

index_url = URLS_CONFIG["reseau"]["couverture_theorique"]
download_from_index(index_url, dest_folder="../data/raw/couverture_theorique", filters=["4G", "5G"])