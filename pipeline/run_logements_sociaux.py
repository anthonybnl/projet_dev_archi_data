"""
Lance le pipeline complet logements sociaux : CSV → silver (enrichi IRIS) → gold.
Usage : python run_logements_sociaux.py
"""

from silver.logements_sociaux.bronze_to_silver import run as run_bronze_to_silver
from gold.logements_sociaux.silver_to_gold import run as run_silver_to_gold


def main():
    print("--- bronze → silver (avec enrichissement IRIS) ---")
    run_bronze_to_silver()

    print("\n--- silver → gold ---")
    run_silver_to_gold()

    print("\npipeline logements sociaux terminé")


if __name__ == "__main__":
    main()
