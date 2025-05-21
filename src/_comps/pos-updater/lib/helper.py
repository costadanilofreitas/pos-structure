import json
import logging
import logging.config
import logging.handlers
import os
import sys

try:
    from StringIO import StringIO  ## for Python 2
except ImportError:
    from io import StringIO  ## for Python 3

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from threading import Lock
from time import sleep
from xml.etree import cElementTree as eTree

import tzlocal
from enum import Enum
from typing import Union, Dict
from unidecode import unidecode


class IsoFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        if fmt is None:
            fmt = "%(asctime)-6s: %(count)2s - %(name)s - %(levelname)s - "\
                  "%(thread)d:%(threadName)s - %(module)s:%(filename)s:%(lineno)s:%(funcName)s - "\
                  "%(message)s"
        super(IsoFormatter, self).__init__(fmt, datefmt)
        self.lock = Lock()
        self.count = 0
        self.max_count = 99

    def get_count(self):
        with self.lock:
            self.count += 1
            if self.count > self.max_count:
                self.count = 1
            return self.count

    def formatTime(self, record, datefmt=None):
        value = datetime.fromtimestamp(record.created, tzlocal.get_localzone())
        base_date = datetime.strftime(value, "%Y-%m-%dT%H:%M:%S")
        base_date += "." + str(int(record.msecs)).zfill(3)
        base_date += datetime.strftime(value, "%z")
        return base_date

    def format(self, record):
        if not hasattr(record, "count"):
            record.count = str(self.get_count()).zfill(2)
        return super(IsoFormatter, self).format(record)


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

    formatter = IsoFormatter()

    comp_logger = logging.getLogger(log_name)
    comp_logger.setLevel(logging.DEBUG)
    comp_logger.propagate = False

    rotating_file_logger = logging.handlers.RotatingFileHandler(filename, 'a', max_size, max_files)
    rotating_file_logger.setLevel(logging.DEBUG)
    rotating_file_logger.setFormatter(formatter)
    comp_logger.addHandler(rotating_file_logger)

    if add_error_handler:
        rotating_file_logger_error = logging.handlers.RotatingFileHandler(filename_error,
                                                                          'a',
                                                                          max_size,
                                                                          max_files)
        rotating_file_logger_error.setLevel(logging.ERROR)
        rotating_file_logger_error.setFormatter(formatter)
        comp_logger.addHandler(rotating_file_logger_error)

    if configure_root:
        root_logger = logging.getLogger()
        root_logger.addHandler(rotating_file_logger)
        root_logger.setLevel(root_level)


def import_pydevd(loader_path, port, suspend=False):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        debug_lib_dir = os.path.join(current_dir, "..", "debug_lib")
        if os.path.exists(debug_lib_dir):
            sys.path.append(debug_lib_dir)
            from debughelper import import_pydevd as real_import_pydevd
            real_import_pydevd(loader_path, port, suspend)
    except ImportError:
        return


def get_path(directory='', file_name_with_extension=''):
    # type: (str, str) -> str
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), directory, file_name_with_extension)


def read_json_from_file_as_dictionary(json_file_path):
    with open(json_file_path, 'rb') as content_file:
        complete_json = content_file.read()
        return json.loads(complete_json.decode("utf-8"))


def remove_accents(text):
    # type: (str) -> str
    if sys.version_info[0] == 2:
        text = unicode(text)
    else:
        text = str(text)

    return unidecode(text)


def json_serialize(obj, simple_enum=None):
    # type: (Any, bool) -> str
    try:
        return json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o) if not simple_enum else ""))
    except ValueError as _:
        return str(obj)


def json_pretty_format(dictionary):
    # type: (Dict) -> str

    return json.dumps(dictionary, sort_keys=True, indent=1, default=lambda o: getattr(o, '__dict__', str(o)))


def retry(logger, method_name, n, sleep_seconds, trying_to_do, is_success, success, failed, on_exception=None):
    for attempt in range(1, n + 1):
        # noinspection PyBroadException
        try:
            logger.debug("Retry [{}] :: trying_to_do {}/{}".format(method_name, attempt, n))
            response = trying_to_do()
            if is_success(response):
                logger.debug("Retry [{}] :: is_success {}/{}".format(method_name, attempt, n))
                return success(response)
            else:
                logger.debug("Retry [{}] :: handle_error {}/{}".format(method_name, attempt, n))
                failed(response)
        except Exception as _:
            logger.exception("Retry [{}] :: EXCEPTION {}/{}".format(method_name, attempt, n))
            if on_exception:
                on_exception()

        sleep(sleep_seconds)

    logger.error("Retry {} :: FAILED after {} tentatives".format(method_name, n))


def dict_to_object(dictionary, obj):
    # type: (dict, object) -> None

    for key in dictionary:
        if hasattr(obj, key):
            setattr(obj, key, dictionary[key])


def build_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))


def get_class_by_name(kls):
    # type: (unicode) -> type
    parts = kls.split(".")
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def remove_xml_namespace(xml):
    # type: (Union[str, unicode]) -> eTree.ElementTree
    it = eTree.iterparse(StringIO(xml))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
    return it.root


def round_half_away_from_zero(number, precision=0):
    number = Decimal(number)
    value = number.quantize(Decimal('10') ** -(precision + 2))
    return float(value.quantize(Decimal('10') ** -precision, rounding=ROUND_HALF_UP))


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
