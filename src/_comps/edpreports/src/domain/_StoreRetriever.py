from abc import ABCMeta, abstractmethod

from _Store import Store  # noqa


class StoreRetriever(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_store(self):
        # type: () -> Store
        raise NotImplementedError()
