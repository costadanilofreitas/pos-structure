from production.model import Item
from typing import Dict

from ._OrderChangerProductionBox import OrderChangerProductionBox


class CollapseSameItemsBox(OrderChangerProductionBox):
    def change_order(self, order):
        new_items = []
        collapsed_items = {}  # type: Dict[str, Item]
        for item in order.items:
            key = self.build_item_key(item)
            if key not in collapsed_items:
                collapsed_items[key] = item
                if not hasattr(item, 'joined_items'):
                    item.joined_items = []
                new_items.append(item)
            else:
                collapsed_items[key].qty += item.qty
                collapsed_items[key].multiplied_qty += item.multiplied_qty
                collapsed_items[key].joined_items.append(item)

        order.items = new_items
        return order

    def build_item_key(self, item, key="", is_parent_product=False):
        # type: (Item, str) -> str
        key += str(item.part_code)
        if len(item.comments) > 0:
            for comment in item.comments.values():
                key += comment.text
        if is_parent_product:
            key += str(item.qty)

        for tag in item.get_tags():
            key += tag

        for son in item.items:
            is_parent_product = item.item_type.upper() == "PRODUCT"
            key += self.build_item_key(son, key, is_parent_product=is_parent_product)

        return key
