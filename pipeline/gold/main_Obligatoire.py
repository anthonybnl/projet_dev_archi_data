import sys
from pathlib import Path

base_path = Path(__file__).resolve().parents[2]
if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))

from pipeline.gold.obligatoire import dfv, filosofi, logements_sociaux


def main():
    print("\n=== GOLD OBLIGATOIRE ===")
    logements_sociaux.run()
    filosofi.run()
    dfv.run()
    print("\nPipeline Gold Obligatoire terminé.")


if __name__ == "__main__":
    main()
