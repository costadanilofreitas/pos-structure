import os
import json
import logging
import logging.config
import logging.handlers
import sys

from enum import Enum


def config_logger(loader_path,
                  log_name='component',
                  configure_root=False,
                  root_level=logging.WARN,
                  max_files=5,
                  max_size=5242880,
                  add_error_handler=False):
    real_path = os.path.realpath(loader_path)
    if os.path.isdir(real_path):
        dir_path = real_path
    else:
        dir_path = os.path.dirname(real_path)

    filename = os.path.join(dir_path, log_name + '.log')
    filename_error = os.path.join(dir_path, log_name + '.error.log')

    formatter = logging.Formatter("%(asctime)-6s: %(name)s - %(levelname)s - "
                                  "%(thread)d - %(threadName)s - %(filename)s:%(lineno)s:%(funcName)s - "
                                  "%(message)s")

    comp_logger = logging.getLogger(log_name)
    comp_logger.setLevel(logging.DEBUG)

    rotating_file_logger = logging.handlers.RotatingFileHandler(filename, 'a', max_size, max_files, encoding="utf-8")
    rotating_file_logger.setLevel(logging.DEBUG)
    rotating_file_logger.setFormatter(formatter)
    comp_logger.addHandler(rotating_file_logger)

    if add_error_handler:
        rotating_file_logger_error = logging.handlers.RotatingFileHandler(filename_error,
                                                                          'a',
                                                                          max_size,
                                                                          max_files,
                                                                          encoding="utf-8")
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
            with open(filename, "r") as debug_file:
                pydev_path = debug_file.read()
            if os.path.exists(pydev_path):
                try:
                    sys.path.index(pydev_path)
                except:
                    sys.path.append(pydev_path)

                import pydevd
                pydevd.settrace('localhost', port=port, stdoutToServer=True, stderrToServer=True, suspend=suspend)


def get_path(directory='', file_name_with_extension=''):
    # type: (str, str) -> str
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), directory, file_name_with_extension)


def read_json_from_file_as_dictionary(json_file_path):
    with open(json_file_path, 'rb') as content_file:
        complete_json = content_file.read()
        return json.loads(complete_json.decode("utf-8"))


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
