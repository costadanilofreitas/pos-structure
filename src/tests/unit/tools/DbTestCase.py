import unittest
import sqlite3
import abc


class DbTestCase(unittest.TestCase):
    __metaclass__ = abc.ABCMeta

    def execute_in_transaction(self, method, database_path, params=None):
        conn = None
        try:
            conn = sqlite3.connect(database_path)
            cur = conn.cursor()

            method(cur, params)

            cur.close()
            conn.commit()
            conn.close()
        except:
            if conn is not None:
                conn.rollback()
                conn.close()

            raise

    def execute_with_clean_database(self, method, params=None):
        def clean_database_and_execute(cur):
            self.clean_database(cur)
            method(cur)

        self.execute_in_transaction(clean_database_and_execute, params)
