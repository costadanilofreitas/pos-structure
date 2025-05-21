from abc import ABCMeta, abstractmethod
from logging import Logger
from threading import Thread

from production.model import ProductionOrder


class ProductionView(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, logger):
        # type: (str, Logger) -> None
        self.name = name
        self.logger = logger
        if self.logger is not None:
            self.log_level = {
                "debug": self.logger.debug,
                "error": self.logger.error,
                "exception": self.logger.exception
            }

    @abstractmethod
    def handle_order(self, order):
        # type: (ProductionOrder) -> Thread
        raise NotImplementedError()

    def debug(self, msg, *args):
        self.log("debug", msg, *args)

    def error(self, msg, *args):
        self.log("error", msg, *args)

    def exception(self, msg, *args):
        self.log("exception", msg, *args)

    def log(self, level, msg, *args):
        if self.logger is not None:
            func = self.log_level[level]
            msg = msg.format(*args)
            func(msg)
