import os
from dotenv import load_dotenv
import py7zr
import geopandas as gpd
from shapely.geometry import box
from download import function_unzip, download_file

load_dotenv(dotenv_path="url.env")

URLS_CONFIG = {
    "reseau": {
        "debit_fibre": os.getenv("ENV_ARBRE_URL"),
        "antenne_reseau": os.getenv("ENV_ESPACE_VERT_URL"),
        "ilots_fraicheur": os.getenv("ENV_ILOTS_FRAICHEUR_ULR"),
        "dechets_trilib": os.getenv("ENV_DECHETS_TRILIB_URL")
    }
}

for key, value in URLS_CONFIG.items():
    for v in value.values():
        url = v
        path = download_file(url)
        function_unzip(path)