import os
from sqlalchemy import text
from pipeline.db import get_engine, ensure_schemas

SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql")


def run_sql_file(conn, path):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.execute(text(sql))


def run(engine):
    ensure_schemas(engine)
    with engine.connect() as conn:
        for layer in ("silver", "gold"):
            layer_dir = os.path.join(SQL_DIR, layer)
            if not os.path.isdir(layer_dir):
                continue
            for filename in sorted(os.listdir(layer_dir)):
                if filename.endswith(".sql"):
                    path = os.path.join(layer_dir, filename)
                    run_sql_file(conn, path)
                    print(f"[init_db] {layer}/{filename} ✓")
        conn.commit()
    print("[init_db] Toutes les tables sont prêtes.")


if __name__ == "__main__":
    run(get_engine())
