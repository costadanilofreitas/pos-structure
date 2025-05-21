from abc import ABCMeta, abstractmethod

from pos_model import SaleItem, TaxItem
from typing import List, Tuple


class TaxCalculator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_tax(self, item, previous_taxes):
        # type: (SaleItem, List[Tuple[SaleItem, TaxItem]]) -> TaxItem
        raise NotImplementedError()

    def create_base_tax_item(self, sale_item):
        # type: (SaleItem) -> TaxItem
        tax_item = TaxItem()
        tax_item.line_number = sale_item.line_number
        tax_item.level = sale_item.level
        tax_item.item_id = sale_item.item_id
        tax_item.part_code = sale_item.part_code

        return tax_item
