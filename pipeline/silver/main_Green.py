import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.silver import arbres, espaces_verts, ilots_fraicheur, trilib

def main():
    arbres.main()
    espaces_verts.main()
    ilots_fraicheur.main()
    trilib.main()

if __name__ == "__main__":
    main()