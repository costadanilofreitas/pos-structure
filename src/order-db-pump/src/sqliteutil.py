import os
import os.path
from abc import ABCMeta
from sqlite3 import connect, Cursor, Row, Connection

import unitofwork
from typing import Callable, Any, Optional


class BaseRepository(object):
    __metaclass__ = ABCMeta

    def __init__(self, conn):
        # type: (Connection) -> None
        self.conn = conn

    def close(self):
        self.conn.close()

    def get_scalar(self, sql):
        def inner_func(cursor):
            # type: (Cursor) -> int
            return cursor.execute(sql).fetchone()[0]

        return self.execute_with_cursor(inner_func)

    def execute(self, sql, params=(), mapper=None):
        # type: (str, tuple, Optional[Callable[[Row], Any]]) -> int
        if mapper is None:
            return self.execute_scalar(sql, params)
        else:
            return self.execute_query(sql, params, mapper)

    def execute_query(self, sql, params, mapper):
        # type: (str, tuple, Optional[Callable[[Row], Any]]) -> int
        def inner_func(cursor):
            # type: (Cursor) -> None
            ret = []
            for row in cursor.execute(sql, params):
                ret.append(mapper(row))
            return ret

        return self.execute_with_cursor(inner_func)

    def execute_scalar(self, sql, params):
        # type: (str, tuple) -> int
        def inner_func(cursor):
            # type: (Cursor) -> None
            return cursor.execute(sql, params).rowcount

        return self.execute_with_cursor(inner_func)

    def execute_with_cursor(self, method):
        # type: (Callable[[Cursor], Any]) -> Any
        cursor = None
        try:
            cursor = self.conn.cursor()
            return method(cursor)
        finally:
            if cursor is not None:
                cursor.close()


class DdlExecutor(object):
    __metaclass__ = ABCMeta

    def execute_ddl(self, cursor):
        # type: (Cursor) -> None
        raise NotImplementedError


class DatabaseCreator(object):
    __metaclass__ = ABCMeta

    def __init__(self, file_path, ddl_executor):
        # type: (str, DdlExecutor) -> None
        self.file_path = file_path
        self.ddl_executor = ddl_executor

    def create_database(self):
        must_create = not os.path.isfile(self.file_path)
        directory = os.path.dirname(self.file_path)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        if must_create:
            conn = connect(self.file_path)
            cursor = None
            try:
                cursor = conn.cursor()
                self.ddl_executor.execute_ddl(cursor)
            except:
                if cursor is not None:
                    cursor.close()
                    cursor = None
                if conn is not None:
                    conn.close()
                    conn = None
                os.remove(self.file_path)
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()


class DefaultDdlExecutor(DdlExecutor):
    def __init__(self, query):
        self.query = query

    def execute_ddl(self, cursor):
        for query in self.query.split(";"):
            cursor.execute(query)


class TransactionManager(unitofwork.TransactionManager):
    def __init__(self, conn):
        # type: (Connection) -> None
        self.conn = conn

    def begin_transaction(self):
        pass

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
