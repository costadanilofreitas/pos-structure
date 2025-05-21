from abc import ABCMeta, abstractmethod


class TableReleaser(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def release_all(self, pos_id):
        # type: (str) -> None
        raise NotImplementedError()
