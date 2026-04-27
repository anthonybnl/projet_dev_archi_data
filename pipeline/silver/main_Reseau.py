import sys
from pathlib import Path

base_path = Path(__file__).resolve().parents[2]

if not str(base_path) in sys.path:
    sys.path.insert(0, str(base_path))

from pipeline.db import get_engine
from pipeline.silver.reseau import fibre, mobile, qualite


def run_silver(engine):
    print("\n=== SILVER ===")
    fibre.run(engine)
    mobile.run(engine)
    qualite.run(engine)


def main():
    engine = get_engine()
    run_silver(engine)
    print("\nPipeline Silver terminé.")


if __name__ == "__main__":
    main()
