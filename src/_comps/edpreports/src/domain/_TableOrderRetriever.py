from abc import ABCMeta, abstractmethod
from ._Table import Table  # noqa


class TableOrderRetriever(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_table_order(self, pos_id, table_id):
        # type: (str, str) -> Table
        raise NotImplementedError()
