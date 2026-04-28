import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.db import get_engine
from pipeline.gold.AES.arrondissement import run as run_arrondissement


def main():
    engine = get_engine()
    print("\n=== GOLD AES ===")
    run_arrondissement(engine)
    print("\nPipeline Gold AES terminé.")


if __name__ == "__main__":
    main()
