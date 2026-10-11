import duckdb
import pandas as pd
import os

DB_PATH = 'data/analytics.duckdb'

def get_connection():
    os.makedirs('data', exist_ok=True)
    return duckdb.connect(DB_PATH)

def load_dataframe(df: pd.DataFrame, table_name: str):
    """Load a Pandas DF into DuckDB as a table."""
    con = get_connection()
    con.register('tmp_df', df)
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM tmp_df")
    con.unregister('tmp_df')
    con.close()
    return True

def list_tables():
    con = get_connection()
    try:
        rows = con.execute("SHOW TABLES").fetchall()
        return [r[0] for r in rows]
    finally:
        con.close()

def table_info(name):
    con = get_connection()
    try:
        cnt = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        cols = con.execute(f"DESCRIBE {name}").fetchdf()
        return cnt, cols
    finally:
        con.close()

def run_query(sql: str):
    con = get_connection()
    try:
        return con.execute(sql).fetchdf()
    finally:
        con.close()

def drop_table(name):
    con = get_connection()
    try:
        con.execute(f"DROP TABLE IF EXISTS {name}")
    finally:
        con.close()

def load_csv(path, table_name):
    df = pd.read_csv(path)
    return load_dataframe(df, table_name)