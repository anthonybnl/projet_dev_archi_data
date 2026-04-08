import os
import re
import zipfile
import py7zr
import requests
from pathlib import Path
from dotenv import load_dotenv

# On spécifie le nom du fichier car il ne s'appelle pas ".env"
load_dotenv(dotenv_path="url.env")

def download_file(url, dest_folder="../data/raw"):
    """
    Télécharge un fichier en récupérer son vrai nom
    via les en-têtes HTTP ou l'URL.
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
        filename = url.split("/")[-1].split("?")[0]

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


def function_unzip(file_path, extract_to="../data/raw"):
    """
    Vérifie si le fichier est une archive, l'extrait et supprime l'original.
    """
    file_path = Path(file_path)
    extract_path = Path(extract_to)

    if not file_path.exists():
        print(f"Erreur : Le fichier {file_path} n'existe pas.")
        return False

    compressed_extensions = ['.zip', '.7z', '.rar', '.gz']

    if file_path.suffix.lower() not in compressed_extensions:
        print(f"L'extension du fichier: {file_path.name} n'est pas une archive reconnue.")
        return False

    try:
        # On crée un sous-dossier au nom du fichier pour éviter de mélanger les fichiers extraits
        final_dest = extract_path
        final_dest.mkdir(parents=True, exist_ok=True)

        if file_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(final_dest)

        elif file_path.suffix.lower() == '.7z':
            with py7zr.SevenZipFile(file_path, mode='r') as z:
                z.extractall(path=final_dest)
        print(f"Extraction réussie dans : {final_dest}")
        file_path.unlink()
        return True

    except Exception as e:
        print(f" Erreur lors de l'extraction de {file_path.name}: {e}")
        return False
