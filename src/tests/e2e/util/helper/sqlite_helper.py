# -*- coding: utf-8 -*-

import os
import sqlite3

from model import DatabaseModel
from typing import Optional, Union, List

DB_PATH = None


def set_db_path(data_dir):
    global DB_PATH
    DB_PATH = data_dir


def get_db_path(db_name, instance_number="", db_path=None):
    # type: (DatabaseModel, int, Optional[str]) -> unicode
    return os.path.abspath(os.path.join(db_path or DB_PATH, "{}.db{}".format(db_name, str(instance_number))))


def execute_query(query, db_name, commit=False, instance_number="", db_path=None):
    # type: (str, DatabaseModel, bool, int, str) -> Union[List, None]
    conn = None
    try:
        database_path = get_db_path(db_name, instance_number, db_path)
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        if commit:
            cursor.executescript(query)
            conn.commit()
        else:
            cursor.execute(query)
            result = cursor.fetchall()
            if result:
                return result
    except Exception as ex:
        if conn:
            conn.rollback()
        raise ex
    finally:
        if conn:
            conn.close()
