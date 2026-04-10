"""
Télécharge les fichiers Filosofi IRIS (revenus disponibles) depuis insee.fr.
Usage : python download_filosofi.py

Les fichiers sont téléchargés dans data/raw/filosofi/ et décompressés automatiquement.
"""

import sys
import zipfile
import io
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import requests as req
from config import DATA_RAW

OUTPUT_DIR = DATA_RAW / "filosofi"

# les URLs changent légèrement selon les millésimes
# on a vérifié chaque page INSEE pour récupérer les bons chemins
FICHIERS = {
    2021: "https://www.insee.fr/fr/statistiques/fichier/8229323/BASE_TD_FILO_IRIS_2021_DISP_CSV.zip",
    2020: "https://www.insee.fr/fr/statistiques/fichier/7233950/BASE_TD_FILO_DISP_IRIS_2020_CSV.zip",
    2019: "https://www.insee.fr/fr/statistiques/fichier/6049648/BASE_TD_FILO_DISP_IRIS_2019.zip",
    2018: "https://www.insee.fr/fr/statistiques/fichier/5055909/BASE_TD_FILO_DISP_IRIS_2018.zip",
}


def telecharger_et_extraire(annee, url):
    # on vérifie si un CSV pour cette année existe déjà
    csvs_existants = list(OUTPUT_DIR.glob(f"*DISP*{annee}*.csv"))
    if csvs_existants:
        print(f"  {annee} : déjà présent ({csvs_existants[0].name})")
        return

    print(f"  {annee} : téléchargement...")
    response = req.get(url, timeout=60)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        # on ne garde que le CSV principal, pas le fichier meta
        for name in zf.namelist():
            if name.endswith(".csv") and "meta" not in name.lower():
                zf.extract(name, OUTPUT_DIR)
                print(f"  {annee} : extrait → {name}")


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"téléchargement des fichiers Filosofi IRIS dans {OUTPUT_DIR}")

    for annee, url in sorted(FICHIERS.items()):
        try:
            telecharger_et_extraire(annee, url)
        except Exception as e:
            print(f"  {annee} : erreur — {e}")

    print("téléchargement terminé")


if __name__ == "__main__":
    run()
