import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def get_engine():
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    name = os.environ.get("DB_NAME")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    return create_engine(url)

def append_table(df, table_name, engine, schema):
    df.to_sql(table_name, engine, schema=schema, if_exists="append", index=False)


def insert_if_empty(df, table_name, engine, schema):
    """Insère les données uniquement si la table est vide, sinon ne fait rien."""
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table_name}")).scalar()
    if count == 0:
        df.to_sql(table_name, engine, schema=schema, if_exists="append", index=False)
        return True
    return False


def insert_ignore(df, table_name, engine, schema):
    """Insère uniquement les nouvelles lignes, ignore les conflits."""
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy import Table, MetaData

    metadata = MetaData()
    table = Table(table_name, metadata, schema=schema, autoload_with=engine)

    # Remplacer NaN/NaT par None pour PostgreSQL
    df = df.astype(object).where(df.notna(), other=None)

    with engine.connect() as conn:
        for record in df.to_dict(orient="records"):
            stmt = pg_insert(table).values(record).on_conflict_do_nothing()
            conn.execute(stmt)
        conn.commit()
