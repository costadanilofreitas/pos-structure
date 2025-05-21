from logging import Logger

from mwrepository import ProductRepository
from production.manager import OrderChanger
from production.view import ProductionView, KdsView
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from typing import List


class ItemSorterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, product_repository, sort_order, logger=None):
        # type: (str, ProductionView, ProductRepository, List[str], Logger) -> None
        super(ItemSorterBox, self).__init__(name, sons, logger)
        self.sort_order = {line: product_repository.get_part_codes_of_jit_lines([line]) for line in sort_order}
        # self.debug("ItemSorterBoxInit sort_order = {}".format(self.sort_order))

    def change_order(self, order):
        order_items = order.items
        order.items = []
        for jit_line in self.sort_order:
            items_to_remove = []
            for item in order_items:
                if item.level > 0:
                    continue
                if item.part_code in self.sort_order[jit_line]:
                    order.items.append(item)
                    items_to_remove.append(item)
            for item in items_to_remove:
                order_items.remove(item)

        for item in order_items:
            order.items.append(item)

        return order
