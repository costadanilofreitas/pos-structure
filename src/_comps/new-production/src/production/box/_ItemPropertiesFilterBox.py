from production.model import Item
from typing import Any

from ._AllowedForbiddenFilter import AllowedForbiddenFilter
from ._OrderChangerProductionBox import OrderChangerProductionBox


class ItemPropertiesFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_properties, forbidden_properties, allow_combos, logger=None):
        super(ItemPropertiesFilterBox, self).__init__(name, sons, logger)
        self.allowed_forbidden_filter = AllowedForbiddenFilter(allowed_properties, forbidden_properties)
        self.allow_combos = allow_combos.lower() == "true"

    def change_order(self, order):
        return self.allowed_forbidden_filter.filter_items(order, self.item_properties_retriever, self.allow_combos)

    def item_properties_retriever(self, item):
        # type: (Item) -> Any
        ret = []
        for p in item.properties:
            ret.append(p)

        return ret
