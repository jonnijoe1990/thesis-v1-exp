import duckdb

class DB:
    def __init__(self, path: str):
        self.con = duckdb.connect(path)

    def __enter__(self):
        return self.con

    def __exit__(self, exc_type, exc_value, traceback):
        self.con.close()

    def __del__(self):
        self.con.close()