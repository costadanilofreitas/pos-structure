from abc import ABCMeta, abstractmethod

from typing import List, Tuple, Dict


class ProductRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_part_codes_of_jit_lines(self, jit_lines):
        # type: (List[str]) -> List[int]
        raise NotImplementedError()

    @abstractmethod
    def get_combos_to_keep(self):
        # type: () -> List[int]
        raise NotImplementedError()

    @abstractmethod
    def get_master_product_map(self):
        # type: () -> Dict[int, Tuple[int, str]]
        raise NotImplementedError()

    def get_prep_times(self):
        # type: () -> Dict[int, int]
        raise NotImplementedError()

    def get_courses_products(self):
        # type: () -> Dict[str, int]
        raise NotImplementedError()

    def get_not_show_on_kitchen(self):
        # type: () -> List[int]
        raise NotImplementedError()

    def get_no_jit_part_codes(self):
        # type: () -> List[int]
        raise NotImplementedError()

    def get_cfh_items(self):
        # type: () -> List[int]
        raise NotImplementedError()

    def get_product_points(self):
        # type: () -> Dict[int, int]
        raise NotImplementedError()
