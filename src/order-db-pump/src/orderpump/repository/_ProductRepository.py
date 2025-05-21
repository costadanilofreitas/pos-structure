from abc import ABCMeta, abstractmethod


class ProductRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_category(self, part_code):
        # type: (int) -> str
        raise NotImplementedError()

    @abstractmethod
    def get_sub_category(self, part_code):
        # type: (int) -> str
        raise NotImplementedError()
