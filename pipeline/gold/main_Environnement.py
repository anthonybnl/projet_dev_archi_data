import sys
from pathlib import Path

base_path = Path(__file__).resolve().parents[2]
if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))

from pipeline.gold.environnement import main as run_environnement


def main():
    print("\n=== GOLD ENVIRONNEMENT ===")
    run_environnement()
    print("\nPipeline Gold Environnement terminé.")


if __name__ == "__main__":
    main()
