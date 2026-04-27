import sys
from pathlib import Path

base_path = Path(__file__).resolve().parents[2]
if not base_path in sys.path:
    sys.path.insert(0, str(base_path))

from pipeline.db import get_engine
from pipeline.silver.mobilite import map_arrets, map_gares, map_velib

def run_silver(engine):
    print("\n=== SILVER ===")
    map_arrets.run(engine)
    map_gares.run(engine)
    map_velib.run(engine)


def main():
    engine = get_engine()
    run_silver(engine)
    print("\nPipeline Silver terminé.")


if __name__ == "__main__":
    main()
