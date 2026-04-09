from pipeline.db import get_engine
from pipeline import init_db
from pipeline.silver import ecoles, colleges, population, sante, map_scolaire, map_sante


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
    init_db.run(engine)
    run_silver(engine)
    print("\nPipeline Silver terminé.")


if __name__ == "__main__":
    main()
