from mw_helper import convert_to_dict, ensure_list
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import Item
from typing import List


class ComboFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, items_to_keep, logger=None):
        super(ComboFilterBox, self).__init__(name, sons, logger)
        self.items_to_keep = convert_to_dict(ensure_list(items_to_keep))

    def change_order(self, order):
        filtered_items = []  # type: List[Item]
        for item in order.items:
            self.handle_item(item, filtered_items, 0)
        order.items = filtered_items

        return order

    def handle_item(self, item, filtered_items, levels_to_subtract, parent_qty=None):
        if parent_qty is not None:
            item.qty *= parent_qty

        if item.item_type in ("PRODUCT", "CANADD"):
            if not hasattr(item, "original_level"):
                item.original_level = item.level
            item.level = int(item.level) - levels_to_subtract
            filtered_items.append(item)
        elif item.item_type in ("COMBO", "OPTION"):
            if item.item_type == "COMBO" and item.part_code in self.items_to_keep:
                filtered_items.append(item)
            elif item.item_type == "OPTION":
                filtered_items.append(item)
            else:
                for son in item.items:
                    self.handle_item(son, filtered_items, levels_to_subtract + 1, item.qty)
