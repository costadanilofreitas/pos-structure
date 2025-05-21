from logging import Logger

from mw_helper import convert_to_dict, ensure_list
from production.box import ProductionBox
from production.model import \
    ProductionOrder
from typing import List, Union

from ._OrderChangerProductionBox import OrderChangerProductionBox


class DoneWhenAnyDoneBox(OrderChangerProductionBox):
    def __init__(self, name, sons, part_codes, logger=None):
        # type: (str, Union[List[ProductionBox], ProductionBox], Union[str, List[str]], Logger) -> None
        super(DoneWhenAnyDoneBox, self).__init__(name, sons, logger)
        self.part_codes = convert_to_dict(ensure_list(part_codes))

    def change_order(self, order):
        if self.has_done_items(order):
            tracked_items = self.get_tracked_items(order)
            self.add_done_on_tracked_items(tracked_items)

        return order

    def has_done_items(self, order):
        # type: (ProductionOrder) -> bool
        for item in order.items:
            if self.has_any_done(item):
                return True

        return False

    def has_any_done(self, item):
        if item.part_code not in self.part_codes and item.has_tag("done") or item.has_tag("served"):
            return True
        for son in item.items:
            if self.has_any_done(son):
                return True

        return False

    def get_tracked_items(self, order, tracked_items=None):
        if tracked_items is None:
            tracked_items = []
        for item in order.items:
            if item.part_code in self.part_codes:
                tracked_items.append(item)
            else:
                for son in item.items:
                    self.get_tracked_items(son, tracked_items)

        return tracked_items

    def add_done_on_tracked_items(self, tracked_items):
        for item in tracked_items:
            if item.does_not_have_tag("done") and item.does_not_have_tag("served"):
                item.add_tag("done")
