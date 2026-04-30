"""
Point d'entrée unique pour exécuter le pipeline complet ou par couche.

Usage :
    python pipeline/run_all.py                        # toutes les couches
    python pipeline/run_all.py --layers nosql         # nosql uniquement
    python pipeline/run_all.py --layers silver gold   # silver puis gold
    python pipeline/run_all.py --layers raw nosql     # raw puis nosql
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ALL_LAYERS = ["raw", "nosql", "silver", "gold"]


def step(label: str):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")


def run_raw():
    step("RAW — Téléchargement des données")
    from pipeline.raw.download import load_config, parallel_download_routing
    config = load_config()
    for section in config.keys():
        parallel_download_routing(config[section], section)


def run_nosql():
    step("NOSQL — Chargement GeoJSON dans MongoDB")
    from no_sql.iris_arr__mongodb import charger_arrondissements, charger_iris
    from no_sql.fonction_no_sql import get_mongo_client, get_database
    client = get_mongo_client()
    db = get_database(client)
    charger_arrondissements(db)
    charger_iris(db)
    client.close()


def run_silver():
    step("SILVER — Obligatoire (DVF, FILOSOFI, Logements sociaux)")
    from pipeline.silver.main_Obligatoire import main as silver_obligatoire
    silver_obligatoire()

    step("SILVER — Environnement")
    from pipeline.silver.main_Environnement import main as silver_env
    silver_env()

    step("SILVER — Mobilité")
    from pipeline.silver.main_Mobilite import main as silver_mobilite
    silver_mobilite()

    step("SILVER — Réseau")
    from pipeline.silver.main_Reseau import main as silver_reseau
    silver_reseau()

    step("SILVER — AES (Éducation, Santé)")
    from pipeline.silver.main_AES import main as silver_aes
    silver_aes()


def run_gold():
    step("GOLD — Obligatoire (DVF, FILOSOFI, Logements sociaux)")
    from pipeline.gold.main_Obligatoire import main as gold_obligatoire
    gold_obligatoire()

    step("GOLD — Environnement")
    from pipeline.gold.main_Environnement import main as gold_env
    gold_env()

    step("GOLD — Mobilité")
    from pipeline.gold.main_Mobilite import main as gold_mobilite
    gold_mobilite()

    step("GOLD — Réseau")
    from pipeline.gold.main_Reseau import main as gold_reseau
    gold_reseau()

    step("GOLD — AES (Éducation, Santé)")
    from pipeline.gold.main_AES import main as gold_aes
    gold_aes()


RUNNERS = {
    "raw": run_raw,
    "nosql": run_nosql,
    "silver": run_silver,
    "gold": run_gold,
}


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Urban Data Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""exemples :
  python pipeline/run_all.py
  python pipeline/run_all.py --layers nosql
  python pipeline/run_all.py --layers silver gold
  python pipeline/run_all.py --layers raw nosql silver gold""",
    )
    parser.add_argument(
        "--layers",
        nargs="+",
        choices=ALL_LAYERS,
        default=ALL_LAYERS,
        metavar="LAYER",
        help="Couches à exécuter parmi : raw nosql silver gold (défaut : toutes)",
    )
    args = parser.parse_args()

    # Respecter l'ordre canonique même si l'utilisateur les donne dans le désordre
    layers = [l for l in ALL_LAYERS if l in args.layers]

    start = time.time()
    print(f"\nDémarrage pipeline Urban Data Explorer — {datetime.now()}")
    print(f"Couches sélectionnées : {' → '.join(layers)}")

    for layer in layers:
        RUNNERS[layer]()

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"  Pipeline terminé en {elapsed/60:.1f} minutes")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
