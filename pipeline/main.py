from pipeline.db import get_engine
from pipeline import init_db
from pipeline.silver import (
    ecoles, colleges, population, sante, map_scolaire, map_sante,
    reseau_mobile, reseau_qualite, reseau_fibre,
)
from pipeline.gold import score_reseau


def run_silver(engine):
    print("\n=== SILVER ===")
    ecoles.run(engine)
    colleges.run(engine)
    population.run(engine)
    sante.run(engine)
    map_scolaire.run(engine)
    map_sante.run(engine)

    # Réseau: les trois tables doivent être insérées avant le score gold
    reseau_mobile.run(engine)
    reseau_qualite.run(engine)
    reseau_fibre.run(engine)


def run_gold(engine):
    print("\n=== GOLD ===")
    # Lit les tables silver reseau_* et produit le score final par IRIS
    score_reseau.run(engine)


def main():
    engine = get_engine()
    init_db.run(engine)
    run_silver(engine)
    #run_gold(engine)
    print("\nPipeline termine.")


if __name__ == "__main__":
    main()
