from datetime import datetime
from mw_helper import ensure_list, convert_to_dict
from production.model import ProdStates, ProductionOrder, Item
from typing import Union, List, Any, Callable, Optional


def _has_value_in_list(list_to_validate, values):
    for v in values:
        if v in list_to_validate:
            return True

    return False


class AllowedForbiddenFilter(object):
    def __init__(self, allowed_values, forbidden_values):
        # type: (Union[Optional[str], List[str]], Union[Optional[str], List[str]]) -> None
        self.allowed_values = None
        self.forbidden_values = None
        if allowed_values is not None:
            self.allowed_values = convert_to_dict(ensure_list(allowed_values))

        if forbidden_values is not None:
            self.forbidden_values = convert_to_dict(ensure_list(forbidden_values))

    def filter_items(self, order, item_value_retriever):
        # type: (ProductionOrder, Callable[[Item], Any]) -> ProductionOrder
        new_items = []
        for item in order.items:
            self.add_item(item, item_value_retriever, new_items)

        order.items = new_items

        return order

    def add_item(self, item, item_value_retriever, new_items):
        values = ensure_list(item_value_retriever(item))
        if self.forbidden_values is not None:
            list_to_validate = self.forbidden_values
            if _has_value_in_list(list_to_validate, values):
                return

        if self.allowed_values is not None:
            list_to_validate = self.allowed_values
            if not _has_value_in_list(list_to_validate, values):
                return

        son_items = []
        for son in item.items:
            self.add_item(son, item_value_retriever, son_items)

        item.items = son_items
        new_items.append(item)
