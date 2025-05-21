from abc import ABCMeta, abstractmethod

from ._Waiter import Waiter


class WaiterRetriever(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_waiter(self, sync_id):
        # type: (int) -> Waiter
        raise NotImplementedError()
