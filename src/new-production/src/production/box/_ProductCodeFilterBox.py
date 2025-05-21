from mw_helper import ensure_iterable

from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import Item, ProductionOrder
from typing import List, Union


class ProductCodeFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, product_codes, keep_children=False, logger=None):
        super(ProductCodeFilterBox, self).__init__(name, sons, logger)
        self.product_codes = ensure_iterable(product_codes)
        self.keep_children = keep_children

    def change_order(self, order):
        self._handle_items(order)

        return order

    def _handle_items(self, item):
        # type: (Union[ProductionOrder, Item]) -> None
        def verify(product):
            return unicode(product.part_code) not in self.product_codes

        new_order_items = []
        for current_item in item.items:
            if verify(current_item):
                new_order_items.append(current_item)

                if current_item.items:
                    self._handle_items(current_item)

            elif str(self.keep_children).lower() == "true":
                for child in current_item.items:
                    child.level = int(child.level) - 1
                    child.qty *= current_item.qty

                    if not verify(child):
                        continue

                    new_order_items.append(child)
                    self._handle_items(child)
        item.items = new_order_items
