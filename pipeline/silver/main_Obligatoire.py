import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.silver.obligatoire import dvf, filosofi, logements_sociaux
def main():
    logements_sociaux.run()
    filosofi.run()
    dvf.run()

if __name__ == "__main__":
    main()