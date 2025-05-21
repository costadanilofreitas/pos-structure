import os
from sqlite3 import connect


class MultipleDatabaseExecutor(object):
    def __init__(self, database_dir):
        self.database_dir = database_dir

    def execute(self, method, repository_class):
        database_files = self.get_database_files()
        for database in database_files:
            conn = connect(database)
            rep = repository_class(conn)

            method(rep)

    def get_database_files(self):
        for _, _, files in os.walk(self.database_dir):
            order_files = []
            for filename in files:
                if filename.startswith("order."):
                    order_files.append(os.path.join(self.database_dir, filename))
            return order_files
