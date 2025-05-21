from abc import ABCMeta, abstractmethod

from messagebus import Event
from typing import List


class Waiter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_sync_id(self):
        # type: () -> str
        raise NotImplementedError()

    def get_events(self):
        # type: () -> List[Event]
        raise NotImplementedError()
