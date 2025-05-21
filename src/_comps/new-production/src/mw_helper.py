from abc import ABCMeta
from datetime import datetime

from dateutil import tz
from msgbus import MBEasyContext
from persistence import Connection, Driver, DbdException
from typing import Callable, Any, List


class BaseRepository(object):
    __metaclass__ = ABCMeta

    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        self.mb_context = mb_context

    def execute_with_connection(self, method, db_name=None, service_name=None):
        # type: (Callable[[Connection], Any], str, str) -> Any

        conn = None
        try:
            db_name = str(db_name) if db_name is not None else None
            conn = Driver().open(self.mb_context, dbname=db_name, service_name=service_name)
            return method(conn)
        finally:
            if conn is not None:
                conn.close()

    def execute_with_transaction(self, method, db_name=None, service_name=None):
        # type: (Callable[[Connection], Any], str, str) -> Any
        def transaction_method(conn):
            # type: (Connection) -> Any

            if conn.get_number_of_instances() != 1 and db_name is None:
                raise DbdException("Cannot open transaction without DB instance")

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


def ensure_iterable(value):
    if isinstance(value, basestring):
        return [value]

    try:
        _ = (e for e in value)
        return value
    except TypeError:
        return [value]


def ensure_list(value):
    if isinstance(value, basestring):
        return [value]

    if isinstance(value, list):
        return value

    try:
        _ = (e for e in value)
        return list(value)
    except TypeError:
        return [value]


def convert_to_dict(iterable):
    ret = {}
    for item in iterable:
        ret[item] = item
    return ret


def convert_from_localtime_to_utc(localtime):
    # type: (datetime) -> datetime
    from_zone = tz.tzlocal()
    to_zone = tz.tzutc()
    localtime = localtime.replace(tzinfo=from_zone)
    utc = localtime.astimezone(to_zone)

    return utc
