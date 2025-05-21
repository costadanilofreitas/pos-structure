import logging
import logging.config
import logging.handlers
import os
import sys
import json

import persistence
from enum import Enum
from typing import Union


def config_logger(loader_path,
                  log_name='component',
                  configure_root=False,
                  root_level=logging.WARN,
                  max_files=5,
                  max_size=5242880,
                  add_error_handler=False):
    real_path = os.path.realpath(loader_path)
    if os.path.isfile(real_path) and real_path.endswith(".ini"):
        logging.config.fileConfig(real_path, disable_existing_loggers=False)
        return

    if os.path.isfile(real_path) and real_path.endswith(".json"):
        with open(real_path, "rb") as f:
            logging.config.dictConfig(json.loads(f.read().decode("utf-8")))
        return

    if os.path.isdir(real_path):
        dir_path = real_path
    else:
        dir_path = os.path.dirname(real_path)

    filename = os.path.join(dir_path, log_name + '.log')
    filename_error = os.path.join(dir_path, log_name + '.error.log')

    log_string = "%(asctime)-6s: %(name)s - %(levelname)s - %(thread)d - %(threadName)s - %(message)s"
    formatter = logging.Formatter(log_string)

    comp_logger = logging.getLogger(log_name)
    comp_logger.setLevel(logging.DEBUG)
    comp_logger.propagate = False

    rotating_file_logger = logging.handlers.RotatingFileHandler(filename, 'a', max_size, max_files)
    rotating_file_logger.setLevel(logging.DEBUG)
    rotating_file_logger.setFormatter(formatter)
    comp_logger.addHandler(rotating_file_logger)

    if add_error_handler:
        rotating_file_logger_error = logging.handlers.RotatingFileHandler(filename_error, 'a', max_size, max_files)
        rotating_file_logger_error.setLevel(logging.ERROR)
        rotating_file_logger_error.setFormatter(formatter)
        comp_logger.addHandler(rotating_file_logger_error)

    if configure_root:
        root_logger = logging.getLogger()
        root_logger.addHandler(rotating_file_logger)
        root_logger.setLevel(root_level)


def import_pydevd(loader_path, port, suspend=False):
    # type: (str, int, bool) -> None
    if "DEBUG" in os.environ:
        dir_path = os.path.dirname(os.path.realpath(loader_path))
        filename = os.path.join(dir_path, "debug.txt")
        if os.path.isfile(filename):
            with open(filename) as debug_file:
                debug_path = debug_file.read()
            if os.path.exists(debug_path):
                if debug_path not in sys.path:
                    sys.path.append(debug_path)

                import pydevd
                pydevd.settrace('localhost', port=port, stdoutToServer=True, stderrToServer=True, suspend=suspend)
            else:
                debug_path = os.path.abspath(debug_path)
                print(debug_path)
                print("path errado")


def get_valid_pricelists(mbcontext):
    price_lists = []
    try:
        conn = persistence.Driver().open(mbcontext)
        cursor = conn.select("SELECT PriceListID FROM Pricelist WHERE CURRENT_DATE BETWEEN EnabledFrom AND EnabledThru")
        for row in cursor:
            pl_id = str(row.get_entry(0) or '')
            price_lists.append(pl_id)
    finally:
        if conn:
            conn.close()
    return price_lists


def unicode_2_ascii(data):
    import unicodedata
    # punctuation = {0x2018: 0x27, 0x2019: 0x27, 0x201C: 0x22, 0x201D: 0x22}
    # data = data.translate(punctuation)
    try:
        data = data.decode('latin_1', 'ignore')
    except:
        pass
    finally:
        data = unicode(data)
        data = unicodedata.normalize('NFKD', data)
        data = data.encode('ascii', 'ignore')
        return data


class ExtendedEnum(Enum):

    @classmethod
    def list_values(cls):
        # type: () -> list
        return list(map(lambda enum: enum.value, cls))

    @classmethod
    def list_names(cls):
        # type: () -> list
        return list(map(lambda enum: enum.name, cls))

    @classmethod
    def list_enums_tuple(cls):
        # type: () -> list
        return list(map(lambda enum: (enum.name, enum.value), cls))

    @classmethod
    def get_name(cls, value):
        # type: (int) -> Union[str, None]
        if value not in cls.list_values():
            return None

        return next(str(enum.name) for enum in cls if enum.value == value)

    @classmethod
    def get_value(cls, name):
        # type: (str) -> Union[int, None]
        if name not in cls.list_names():
            return None

        return next(int(enum.value) for enum in cls if enum.name == name)


class MwOrderStatus(ExtendedEnum):
    IN_PROGRESS = 1
    STORED = 2
    TOTALED = 3
    VOIDED = 4
    PAID = 5
    RECALLED = 6
