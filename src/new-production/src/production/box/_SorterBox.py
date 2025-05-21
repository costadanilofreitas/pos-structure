from typing import Union, Optional, List, Dict
from logging import Logger

from mwrepository import ProductRepository
from production.box import ProductionBox
from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class SorterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, product_repository, sort_order, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], ProductRepository, Dict, Logger) -> None
        super(SorterBox, self).__init__(name, sons, logger)
        self.sort_products = {line: product_repository.get_part_codes_of_jit_lines([line]) for line in sort_order}
        self.sort_order = sort_order

    def change_order(self, order):
        order_items = []

        if order.items:
            for jit, value in sorted(self.sort_order.items(), key=lambda x: x[1]):
                items_to_append = [item for item in order.items if item.part_code in self.sort_products[jit]]
                items_to_append.sort(key=lambda x: x.description)
                order_items.extend(items_to_append)

            if len(order_items) != len(order.items):
                order_items.extend([item for item in order.items if item not in order_items])

        order.items = order_items

        return order
