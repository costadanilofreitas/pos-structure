from mw_helper import ensure_list

from ._OrderChangerProductionBox import OrderChangerProductionBox


class FilterOrderIfNotAllItemsHaveTagBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_tags, forbidden_tags, logger=None):
        super(FilterOrderIfNotAllItemsHaveTagBox, self).__init__(name, sons, logger)
        self.allowed_tags = allowed_tags
        self.forbidden_tags = forbidden_tags

    def change_order(self, order):
        for item in order.items:
            if not item.all_has_at_least_one_tag(self.allowed_tags):
                return None

        all_items_were_printed = True
        for item in order.items:
            for tag in ensure_list(self.forbidden_tags):
                if not item.all_has_at_least_one_tag(ensure_list(tag)):
                    all_items_were_printed = False
        if all_items_were_printed:
            return None

        return order
