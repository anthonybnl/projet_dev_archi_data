import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from download import download_from_index, download_one, load_config

feature_name = "reseau"
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
index_url = os.getenv("ENV_CONVERTURES_THEORIQUE_URL")
download_from_index(index_url, dest_folder="../data/raw/reseau/couverture_theorique", filters=["4G", "5G"])