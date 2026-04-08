import os
from dotenv import load_dotenv
import py7zr
import geopandas as gpd
from shapely.geometry import box
from concurrent.futures import ThreadPoolExecutor, as_completed
from download import function_unzip, download_file, download_from_index, download_one, load_config

load_dotenv(dotenv_path="url.env")

URLS_CONFIG = {
    "mobiliter": {
        "velib": os.getenv("ENV_VELIB_URL"),
        "station_metro": os.getenv("ENV_STATION_METRO_URL"),
        "bus": os.getenv("ENV_BUS_URL"),
        "dechets_trilib": os.getenv("ENV_DECHETS_TRILIB_URL")
    }
}
feature_name = "mobilite"
data_url = load_config()
feature_data = data_url[feature_name]
print(feature_data.values())

urls_simples = [v for v in feature_data.values() if v]

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(download_one, url,f"../data/raw/{feature_name}"): url for url in urls_simples}
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"[ERREUR] {futures[future]} : {e}")