import sys
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]

if not str(BASE_PATH) in sys.path:
    sys.path.insert(0, str(BASE_PATH))

from pipeline.db import get_engine
from pipeline.gold.AES import arrondissement


def main():
    engine = get_engine()
    print("\n=== GOLD AES ===")
    arrondissement.run(engine)
    print("\nPipeline Gold AES terminé.")


if __name__ == "__main__":
    main()
