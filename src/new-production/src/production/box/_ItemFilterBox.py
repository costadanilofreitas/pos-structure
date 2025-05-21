from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import Item
from typing import List


class ItemFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_part_codes, forbidden_part_codes=None, show_all_items="False", logger=None):
        super(ItemFilterBox, self).__init__(name, sons, logger)
        self.allowed_part_codes = allowed_part_codes
        self.forbidden_part_codes = forbidden_part_codes
        self.show_all_items = show_all_items.lower() == 'true'

    def change_order(self, order):
        filtered_items = []  # type: List[Item]
        for item in order.items:
            self.handle_item(item, filtered_items)
        order.items = filtered_items

        return order

    def handle_item(self, item, filtered_items, main_item_allowed=False):
        if self.forbidden_part_codes is not None and self._forbidden_part_code(item.part_code):
            if not self.show_all_items:
                return
            item.add_tag("dont-need-cook")

        is_part_code_allowed = self._allowed_part_code(item.part_code)
        if item.item_type in ("COMBO", "OPTION"):
            sons = []
            main_item_allowed = self.allowed_part_codes and is_part_code_allowed

            for son in item.items:
                self.handle_item(son, sons, main_item_allowed)

            item.items = sons
            filtered_items.append(item)
        else:
            if self.allowed_part_codes is not None and not is_part_code_allowed and not main_item_allowed:
                if not self.show_all_items:
                    return
                item.add_tag("dont-need-cook")

            filtered_items.append(item)

    def _forbidden_part_code(self, part_code):
        return self.forbidden_part_codes and part_code in self.forbidden_part_codes

    def _allowed_part_code(self, part_code):
        return self.allowed_part_codes and part_code in self.allowed_part_codes
