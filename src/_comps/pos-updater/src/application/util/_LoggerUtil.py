from logging import getLogger


class LoggerUtil:
    def __init__(self):
        return

    @staticmethod
    def get_logger_name(name):
        return getLogger(name.split(".")[-1][1:])
