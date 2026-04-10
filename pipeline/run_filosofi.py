"""
Lance le pipeline complet Filosofi : téléchargement → silver → gold (avec calcul IAI).
Usage : python run_filosofi.py

Prérequis : le pipeline DVF doit avoir été lancé avant (gold.indicateurs_dvf_iris rempli).
"""

from download_filosofi import run as run_download
from silver.filosofi.bronze_to_silver import run as run_bronze_to_silver
from gold.filosofi.silver_to_gold import run as run_silver_to_gold


def main():
    print("--- téléchargement des fichiers Filosofi ---")
    run_download()

    print("\n--- bronze → silver ---")
    run_bronze_to_silver()

    print("\n--- silver → gold (calcul IAI) ---")
    run_silver_to_gold()

    print("\npipeline Filosofi terminé")


if __name__ == "__main__":
    main()
