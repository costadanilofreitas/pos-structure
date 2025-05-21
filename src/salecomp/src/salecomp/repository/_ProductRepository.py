from abc import ABCMeta, abstractmethod

from salecomp.model import ProductPart, DefaultOption
from typing import List


class ProductRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_menu_valid(self, menu_id):
        # type: (int) -> bool
        raise NotImplementedError()

    @abstractmethod
    def is_option(self, part_code):
        # type: (int) -> bool
        raise NotImplementedError()

    @abstractmethod
    def is_valid_solution(self, option_part_code, part_code):
        # type: (int, int) -> bool
        raise NotImplementedError()

    @abstractmethod
    def get_max_quantity(self, part_code, son_part_code):
        # type: (int, int) -> int
        raise NotImplementedError()

    @abstractmethod
    def get_parts(self, part_code):
        # type: (int) -> List[ProductPart]
        raise NotImplementedError()

    @abstractmethod
    def get_default_options(self, part_code):
        # type: (int) -> List[DefaultOption]
        raise NotImplementedError()
