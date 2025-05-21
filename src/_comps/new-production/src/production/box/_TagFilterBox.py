from production.box._OrderChangerProductionBox import OrderChangerProductionBox

from ._AllowedForbiddenFilter import AllowedForbiddenFilter


class TagFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_tags, forbidden_tags, allow_combos, logger=None):
        super(TagFilterBox, self).__init__(name, sons, logger)
        self.filter = AllowedForbiddenFilter(allowed_tags, forbidden_tags)
        self.allow_combos = allow_combos.lower() == "true"

    def change_order(self, order):
        order = self.filter.filter_items(order, self.get_item_tag, self.allow_combos)
        return order

    def get_item_tag(self, item):
        return item.get_tags()
