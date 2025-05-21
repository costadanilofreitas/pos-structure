from abc import ABCMeta, abstractmethod
from datetime import datetime


class Clock(object):
    __meta__ = ABCMeta

    @abstractmethod
    def now(self):
        # type: () -> datetime
        raise NotImplementedError()

    @abstractmethod
    def utc_now(self):
        # type: () -> datetime
        raise NotImplementedError()
