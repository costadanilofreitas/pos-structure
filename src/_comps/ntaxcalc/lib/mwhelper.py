import os
from abc import ABCMeta

from msgbus import MBEasyContext
from persistence import Connection, Driver
from typing import Callable, Any, List


class BaseRepository(object):
    __metaclass__ = ABCMeta

    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        self.mb_context = mb_context

    def execute_with_connection(self, method, db_name=None, service_name=None):
        # type: (Callable[[Connection], Any], int, str) -> Any
        conn = None
        try:
            conn = Driver().open(self.mb_context,
                                 dbname=str(db_name) if db_name is not None else None,
                                 service_name=service_name)
            return method(conn)
        finally:
            if conn is not None:
                conn.close()

    def execute_with_transaction(self, method, db_name=None, service_name=None):
        # type: (Callable[[Connection], Any], int, str) -> Any
        def transaction_method(conn):
            # type: (Connection) -> Any

            conn.transaction_start()
            try:
                conn.query("BEGIN TRANSACTION")
                ret = method(conn)
                conn.query("COMMIT")
                return ret
            except:
                conn.query("ROLLBACK")
                raise
            finally:
                conn.transaction_end()

        return self.execute_with_connection(transaction_method, db_name=db_name, service_name=service_name)

    def execute_in_all_databases(self, method, pos_list):
        # type: (Callable[[Connection], Any], List[int]) -> Any
        ret = []
        for pos in pos_list:
            conn = None
            try:
                conn = Driver().open(self.mb_context, dbname=str(pos))
                ret.append(method(conn))
            finally:
                if conn is not None:
                    conn.close()

        return ret

    def execute_in_all_databases_returning_flat_list(self, method, pos_list):
        # type: (Callable[[Connection], Any], List[int]) -> Any
        inner_ret = self.execute_in_all_databases(method, pos_list)

        ret = []
        for inner_list in inner_ret:
            ret.extend(inner_list)

        return ret


def find_value_with_vars(cfg, path, default_value=None):
    value = cfg.find_value(path, default_value)
    if value is None:
        return value

    for variable_name in os.environ:
        variable_format = "{{{}}}".format(variable_name)
        if variable_format in value:
            value = value.replace(variable_format, os.environ[variable_name])
            if variable_name in ("BUNDLEDIR", "HVDATADIR"):
                value = value.replace("/./", os.sep).replace("//", os.sep).replace("/", os.sep)

    return value
