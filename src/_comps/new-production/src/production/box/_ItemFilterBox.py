from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import Item, ProdStates
from typing import List


class ItemFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_part_codes, excluded_part_codes=None, forbidden_part_codes=None,
                 show_all_items="True", logger=None):
        super(ItemFilterBox, self).__init__(name, sons, logger)
        self.allowed_part_codes = allowed_part_codes
        self.excluded_part_codes = excluded_part_codes
        self.forbidden_part_codes = forbidden_part_codes
        self.show_all_items = show_all_items.lower() == 'true'

    def change_order(self, order):
        filtered_items = []  # type: List[Item]
        for item in order.items:
            self.handle_item(item, filtered_items)
        order.items = filtered_items
        if len(order.items) == 0:
            order.prod_state = ProdStates.INVALID

        return order

    def handle_item(self, item, filtered_items, main_item_allowed=False):
        if self.forbidden_part_codes and self._forbidden_part_code(item.part_code):
            return
        
        if self.excluded_part_codes and self._excluded_part_code(item.part_code):
            if self.show_all_items:
                item.add_tag("dont-need-cook")
            else:
                return
        
        if item.item_type == "COMBO" or item.item_type == "OPTION":
            sons = []
            main_item_allowed = self.allowed_part_codes and self._allowed_part_code(item.part_code)
            
            for son in item.items:
                self.handle_item(son, sons, main_item_allowed)

            item.items = sons
            filtered_items.append(item)
        else:
            if self.allowed_part_codes and not self._allowed_part_code(item.part_code) and not main_item_allowed:
                if self.show_all_items:
                    item.add_tag("dont-need-cook")
                else:
                    return
                    
            filtered_items.append(item)
            
    def _forbidden_part_code(self, part_code):
        return part_code in self.forbidden_part_codes
        
    def _excluded_part_code(self, part_code):
        return part_code in self.excluded_part_codes
    
    def _allowed_part_code(self, part_code):
        return part_code in self.allowed_part_codes
