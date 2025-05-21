import os
import logging
import logging.config
import logging.handlers
import sys


def config_logger(loader_path, log_name='component'):
    dir_path = os.path.dirname(os.path.realpath(loader_path))
    filename = os.path.join(dir_path, log_name + '.log')

    formatter = logging.Formatter("%(asctime)-6s: %(name)s - %(levelname)s - "
                                  "%(thread)d - %(threadName)s - %(message)s")

    rotating_file_logger = logging.handlers.RotatingFileHandler(filename, 'a', 5242880, 5)
    rotating_file_logger.setLevel(logging.DEBUG)  # DEBUG Log
    # rotating_file_logger.setLevel(logging.ERROR)  # Production Log
    rotating_file_logger.setFormatter(formatter)

    comp_logger = logging.getLogger()
    comp_logger.addHandler(rotating_file_logger)
    comp_logger.setLevel(logging.DEBUG)


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
