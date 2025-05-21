from datetime import datetime
from production.model import \
    ProductionOrder, \
    ProdStates, \
    Item
from typing import List

from ._OrderChangerProductionBox import OrderChangerProductionBox


class DoneFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(DoneFilterBox, self).__init__(name, sons, logger)

    def change_order(self, order):
        order.items = self.filter_done_items(order)

        return order

    def filter_done_items(self, order):
        # type: (ProductionOrder) -> List[Item]
        done_items = []
        for item in order.items:
            self.add_done_items(item, done_items)
        return done_items

    def add_done_items(self, item, done_items):
        if item.is_product() and item.has_tag("done") and item.does_not_have_tag("served"):
            done_items.append(item)
        else:
            new_sons = []
            for son in item.items:
                self.add_done_items(son, new_sons)
            if len(new_sons) > 0:
                item.items = new_sons
                done_items.append(item)
