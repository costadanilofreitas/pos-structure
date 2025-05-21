from mw_helper import ensure_list, convert_to_dict
from production.model import ProdStates, ProductionOrder, Item
from typing import Union, List, Any, Callable, Optional


class AllowedForbiddenFilter(object):
    def __init__(self, allowed_values, forbidden_values):
        # type: (Union[Optional[str], List[str]], Union[Optional[str], List[str]]) -> None
        self.allowed_values = None
        self.forbidden_values = None
        if allowed_values is not None:
            self.allowed_values = convert_to_dict(ensure_list(allowed_values))

        if forbidden_values is not None:
            self.forbidden_values = convert_to_dict(ensure_list(forbidden_values))

    def filter_items(self, order, item_value_retriever, allow_combos):
        # type: (ProductionOrder, Callable[[Item], Any]) -> ProductionOrder
        new_items = []
        for item in order.items:
            self.add_item(item, item_value_retriever, new_items, allow_combos)

        order.items = new_items
        if len(new_items) == 0:
            order.prod_state = ProdStates.INVALID
        return order

    def add_item(self, item, item_value_retriever, new_items, allow_combos=True):
        forbidden_item = False
        values = ensure_list(item_value_retriever(item))
        if self.forbidden_values is not None:
            for v in values:
                if v in self.forbidden_values:
                    forbidden_item = True
                    break

        if not forbidden_item and self.allowed_values is not None:
            forbidden_item = True
            for v in values:
                if v in self.allowed_values:
                    forbidden_item = False
                    break

        if forbidden_item:
            return

        if forbidden_item and not allow_combos:
            return

        son_items = []
        for son in item.items:
            self.add_item(son, item_value_retriever, son_items, allow_combos)

        item.items = son_items
        new_items.append(item)
