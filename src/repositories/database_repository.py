import os
import sqlite3


class DatabaseRepository:
    def __init__(self, database_file, schema_file):
        db_is_new = not os.path.exists(database_file)
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
        if db_is_new:
            with open(schema_file, 'rt') as f:
                schema = f.read()
            self.connection.executescript(schema)

    def close_db(self):
        self.connection.commit()
        self.connection.close()
