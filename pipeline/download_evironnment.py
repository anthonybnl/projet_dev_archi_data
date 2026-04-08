import os
from dotenv import load_dotenv
import py7zr
import geopandas as gpd
from shapely.geometry import box
from concurrent.futures import ThreadPoolExecutor, as_completed
from download import function_unzip, download_file, download_from_index, download_one

load_dotenv(dotenv_path="url.env")

URLS_CONFIG = {
    "environnement": {
        "arbre": os.getenv("ENV_ARBRE_URL"),
        "espace_vert": os.getenv("ENV_ESPACE_VERT_URL"),
        "ilots_fraicheur": os.getenv("ENV_ILOTS_FRAICHEUR_ULR"),
        "dechets_trilib": os.getenv("ENV_DECHETS_TRILIB_URL")
    }
}

for key, value in URLS_CONFIG.items():
    for v in value.values():
        url = v
        path = download_file(url)
        function_unzip(path)

urls_simples = [v for v in URLS_CONFIG["environnement"].values() if v]

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(download_one, url,"../data/raw/environnement"): url for url in urls_simples}
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"[ERREUR] {futures[future]} : {e}")