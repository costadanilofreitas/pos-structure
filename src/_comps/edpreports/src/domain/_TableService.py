from abc import ABCMeta, abstractmethod


class TableService(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_table_picture(self, pos_id, table_id):
        # type: (str, str) -> str
        raise NotImplementedError()

    @abstractmethod
    def get_tip_rate(self):
        # type: () -> int
        raise NotImplementedError()
