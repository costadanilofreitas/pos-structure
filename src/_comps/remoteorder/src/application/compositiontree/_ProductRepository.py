# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from application.compositiontree import ProductPart
from typing import Dict, List


class ProductRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all_products(self):
        # type: () -> Dict[unicode, unicode]
        pass

    @abstractmethod
    def get_all_combos(self):
        # type: () -> Dict[unicode, unicode]
        pass

    @abstractmethod
    def get_all_options(self):
        # type: () -> Dict[unicode, unicode]
        pass

    @abstractmethod
    def get_all_option_products(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        pass

    @abstractmethod
    def get_all_product_ingredients(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        pass

    # TODO: modificar o nome destes dois métodos
    @abstractmethod
    def get_all_combo_options(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        pass

    @abstractmethod
    def get_all_combo_products(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        pass

    @abstractmethod
    def get_all_combo_combos(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        pass

    @abstractmethod
    def get_default_products(self):
        # type: () -> Dict[(int, int), Dict[int, int]]
        pass

    @abstractmethod
    def get_product_name_dictionary(self):
        # type: () -> Dict[(int, int), Dict[int, int]]
        pass

    @abstractmethod
    def get_unavailable_products(self):
        # type: () -> List[unicode]
        pass
