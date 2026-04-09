import re
import zipfile
import py7zr
import requests
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

#################### DATA LOAD ####################
def load_config(config_file="url_data.yaml",**kwargs):
    with open(config_file, "r", encoding="utf-8") as f:
        # safe_load empêche l'exécution de code arbitraire dans le YAML
        return yaml.safe_load(f)

#################### DOWNLOAD ####################

def download_file(url, dest_folder="../data/raw",**kwargs):
    """
    Télécharge un fichier en récupérer son vrai nom via les en-têtes HTTP ou l'URL.
    """
    path_dest = Path(dest_folder)
    path_dest.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Tentative de récupération du nom via le header Content-Disposition
    filename = None
    content_disp = response.headers.get('Content-Disposition')
    if content_disp:
        fname_match = re.findall('filename=(.+)', content_disp)
        if fname_match:
            filename = fname_match[0].strip('" ')

    # Si non trouvé, on utilise la fin de l'URL
    if not filename:
        final_url = response.url
        filename = final_url.split("/")[-1].split("?")[0]

    file_path = path_dest / filename

    # Si le fichier n'a pas d'extension mais que c'est du ZIP
    content_type = response.headers.get('Content-Type', '').lower()
    if file_path.suffix == '' and 'zip' in content_type:
        file_path = file_path.with_suffix('.zip')
    elif file_path.suffix == '' and '7z' in content_type:
        file_path = file_path.with_suffix('.7z')

    print(f"=== Downloading: {file_path.name} ===")

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Téléchargement terminé : {file_path}")
    return file_path


def function_unzip(file_path, extract_to="../data/raw",**kwargs):
    """
    Vérifie si le fichier est une archive, l'extrait et supprime l'original.
    """
    file_path = Path(file_path)
    extract_path = Path(extract_to)

    if not file_path.exists():
        print(f"Erreur : Le fichier {file_path} n'existe pas.")
        return False

    def change_extension(zipfile, file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # On parcourt chaque fichier dans l'archive
            for member in zip_ref.namelist():
                # Extraction du fichier individuel
                zip_ref.extract(member, final_dest)

                # Gestion du renommage .txt vers .csv
                extracted_file = Path(final_dest) / member
                if extracted_file.suffix.lower() == '.txt':
                    new_file = extracted_file.with_suffix('.csv')
                    # Renomme uniquement si le fichier .csv n'existe pas déjà
                    extracted_file.replace(new_file)
                    print(f"Renommé : {extracted_file.name} -> {new_file.name}")

    compressed_extensions = ['.zip', '.7z', '.rar', '.gz']

    if file_path.suffix.lower() not in compressed_extensions:
        print(f"ℹ{file_path.name} n'est pas une archive (CSV/JSON/Autre). Conservation du fichier brut.")
        return True

    try:
        # On crée un sous-dossier au nom du fichier pour éviter de mélanger les fichiers extraits
        final_dest = extract_path
        final_dest.mkdir(parents=True, exist_ok=True)

        if file_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(final_dest)
                change_extension(zipfile,file_path)
        elif file_path.suffix.lower() == '.7z':
            with py7zr.SevenZipFile(file_path, mode='r') as z:
                z.extractall(path=final_dest)
        print(f"Extraction réussie dans : {final_dest}")
        file_path.unlink()
        return True

    except Exception as e:
        print(f" Erreur lors de l'extraction de {file_path.name}: {e}")
        return False

def download_from_index(index_url, dest_folder="../data/raw", filters=None, **kwargs):
    """
    Scrappe une page d'index Apache, filtre les fichiers selon des mots-clés
    et télécharge + extrait chaque archive trouvée.
    filters: liste de chaînes à chercher dans le nom (ex: ['4G', '5G'])
    """
    response = requests.get(index_url, allow_redirects=True)
    response.raise_for_status()

    base_url = index_url.rstrip("/") + "/"
    links = re.findall(r'href="([^"]+)"', response.content.decode("utf-8", errors="replace"))

    # Garder uniquement les fichiers (pas les dossiers/liens parents)
    file_links = [l for l in links if not l.startswith("http") and not l.startswith("..") and "." in l]

    if filters:
        file_links = [l for l in file_links if any(f in l for f in filters)]

    if not file_links:
        print(f"[SKIP] Aucun fichier trouve avec les filtres {filters}")
        return []

    print(f"[INFO] {len(file_links)} fichier(s) a telecharger en parallele...")

    def download_and_extract(filename, **kwargs):
        url = base_url + filename
        path = download_file(url, dest_folder=dest_folder)
        function_unzip(path, extract_to=dest_folder)
        return path

    downloaded = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(download_and_extract, f): f for f in file_links}
        for future in as_completed(futures):
            try:
                downloaded.append(future.result())
            except Exception as e:
                print(f"[ERREUR] {futures[future]} : {e}")

    return downloaded


def download_one(url,dest_folder, **kwargs):
    path = download_file(url,dest_folder)
    function_unzip(path,dest_folder)

#################### PARALLELISATION ####################
def parallel_download_routing(urls_dict, feature_name, base_path="../data/raw"):
    """
    Parcourt un dictionnaire de type {nom_source: url} et télécharge
    en fonction de la clé.
    """
    dest_folder = Path(base_path) / feature_name
    dest_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n--- Catégorie : {feature_name.upper()} ---")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}

        for key, url in urls_dict.items():
            # Routage vers la fonction spéciale Arcep
            if key == "couvertures_theoriques":
                print(f"Scan d'index détecté pour : {key}")
                dest_folder = "../data/raw/reseau/couverture_theorique"
                futures[executor.submit(download_from_index, url,dest_folder,filters=["4G", "5G"] )] = key

            # Routage vers le téléchargement classique
            else:
                futures[executor.submit(download_one, url, str(dest_folder))] = key

        # Gestion des retours
        for future in as_completed(futures):
            source_name = futures[future]
            try:
                future.result()
                print(f"Terminé : {source_name}")
            except Exception as e:
                print(f"Erreur sur '{source_name}': {e}")