"""
Lance le pipeline complet DVF : fichiers CSV → silver (géocodé + IRIS) → gold.
Usage : python run_dvf.py

Attention : le géocodage peut prendre plusieurs minutes selon le volume de données.
"""

from silver.dvf.bronze_to_silver import run as run_bronze_to_silver
from gold.dvf.silver_to_gold import run as run_silver_to_gold


def main():
    print("--- bronze → silver (avec géocodage + enrichissement IRIS) ---")
    run_bronze_to_silver()

    print("\n--- silver → gold ---")
    run_silver_to_gold()

    print("\npipeline DVF terminé")


if __name__ == "__main__":
    main()
