from db import DB
from pathlib import Path
from duckdb import DuckDBPyConnection

db_path = Path(__file__).parent.parent.joinpath("char_data.db").resolve()

def drop_table_if_exists(con: DuckDBPyConnection, table_name: str):
    con.execute(f"DROP TABLE IF EXISTS {table_name}")

def print_first_five(con: DuckDBPyConnection, table_name: str):
    # example query
    result = con.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchall()

    # print the pairs
    for row in result:
        print(row)

def get_count(con: DuckDBPyConnection, table_name: str) -> int:
    result = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    return result[0]


def main():
    with DB(db_path) as db:
        print_first_five(db, "sap_ish_patient")
        

if __name__ == "__main__":
    main()