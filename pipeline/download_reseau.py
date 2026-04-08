import os
from dotenv import load_dotenv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from download import function_unzip, download_file, download_from_index, download_one

load_dotenv(dotenv_path="url.env")

URLS_CONFIG = {
    "reseau": {
        "debit_fibre": os.getenv("ENV_HAUT_DEBIT_FIBRE_URL"),
        "antenne_reseau": os.getenv("ENV_ANTENNE_RESEAU_URL"),
    }
}

urls_simples = [v for v in URLS_CONFIG["reseau"].values() if v]

# MultiTread max 4 workers simultaner
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(download_one, url,"../data/raw/reseau"): url for url in urls_simples}
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"[ERREUR] {futures[future]} : {e}")

index_url = os.getenv("ENV_CONVERTURES_THEORIQUE_URL")
download_from_index(index_url, dest_folder="../data/raw/reseau/couverture_theorique", filters=["4G", "5G"])