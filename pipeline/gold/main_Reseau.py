import sys
from pathlib import Path

base_path = Path(__file__).resolve().parents[2]
if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))

from pipeline.db import get_engine
from pipeline.gold.reseau import run as run_reseau


def main():
    engine = get_engine()
    print("\n=== GOLD RESEAU ===")
    run_reseau(engine)
    print("\nPipeline Gold Réseau terminé.")


if __name__ == "__main__":
    main()
