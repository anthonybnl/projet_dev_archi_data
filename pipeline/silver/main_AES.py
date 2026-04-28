import sys
from pathlib import Path

base_path = str(Path(__file__).resolve().parents[2])
if not base_path in sys.path:
    sys.path.insert(0, base_path)

from pipeline.db import get_engine
from pipeline.silver.AES import (
    ecoles,
    colleges,
    population,
    sante,
    map_scolaire,
    map_sante,
)


def run_silver(engine):
    print("\n=== SILVER ===")
    ecoles.run(engine)
    colleges.run(engine)
    population.run(engine)
    sante.run(engine)
    map_scolaire.run(engine)
    map_sante.run(engine)


def main():
    engine = get_engine()
    run_silver(engine)
    print("\nPipeline Silver terminé.")


if __name__ == "__main__":
    main()
