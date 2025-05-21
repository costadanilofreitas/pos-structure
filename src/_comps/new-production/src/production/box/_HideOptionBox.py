from production.model import Item
from typing import List, Optional

from ._OrderChangerProductionBox import OrderChangerProductionBox


class HideOptionBox(OrderChangerProductionBox):
    def __init__(self, name, sons, fix_default_qty, logger):
        super(HideOptionBox, self).__init__(name, sons, logger)
        self.fix_default_qty = fix_default_qty

    def change_order(self, order):
        returned_items = []
        for item in order.items:
            new_sons = self.remove_option(item, None)
            returned_items.extend(new_sons)
        order.items = returned_items
        return order

    def remove_option(self, item, father):
        # type: (Item, Optional[Item]) -> Optional[List[Item]]
        new_items = []
        if item.item_type == "OPTION":
            for son in item.items:
                if not hasattr(son, "original_level"):
                    son.original_level = son.level
                son.level -= 1

                if self.fix_default_qty:
                    product_or_combo = father and (father.item_type == "COMBO" or father.item_type == "PRODUCT")
                    if product_or_combo and item.default_qty > 0:
                        son.default_qty = son.qty

                if son.default_qty == 0 and son.qty == 0:
                    continue

                new_items.append(son)

            returned_items = []
            for son in new_items:
                new_sons = self.remove_option(son, item)
                returned_items.extend(new_sons)
            return returned_items

        filtered_sons = []
        for son in item.items:
            filtered_sons.extend(self.remove_option(son, item))
        item.items = filtered_sons
        return [item]
