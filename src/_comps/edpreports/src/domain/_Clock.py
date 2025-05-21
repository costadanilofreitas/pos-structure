from abc import ABCMeta, abstractmethod

from datetime import datetime  # noqa


class Clock(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_current_date(self):
        # type: () -> datetime
        raise NotImplementedError()

    @abstractmethod
    def get_current_datetime(self):
        # type: () -> datetime
        raise NotImplementedError()
