from abc import ABCMeta, abstractmethod

from ._Report import Report


class Formatter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def format(self, report):
        # type: (Report) -> bytes
        raise NotImplementedError()
