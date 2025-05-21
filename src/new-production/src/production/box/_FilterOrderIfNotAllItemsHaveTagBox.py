from mw_helper import ensure_iterable

from ._OrderChangerProductionBox import OrderChangerProductionBox


class FilterOrderIfNotAllItemsHaveTagBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_tags, forbidden_tags, remove_order, logger=None):
        super(FilterOrderIfNotAllItemsHaveTagBox, self).__init__(name, sons, logger)
        self.allowed_tags = ensure_iterable(allowed_tags)
        self.forbidden_tags = ensure_iterable(forbidden_tags)
        self.remove_order = remove_order

    def change_order(self, order):
        if self._has_not_allowed_tag(order) or self._has_forbidden_tag(order):
            if self.remove_order:
                return None
            else:
                order.items = []

        return order

    def _has_not_allowed_tag(self, order):
        if len(self.allowed_tags) > 0:
            for item in order.items:
                if not item.all_has_at_least_one_tag(self.allowed_tags):
                    return True

        return False

    def _has_forbidden_tag(self, order):
        if len(self.forbidden_tags) > 0:
            for item in order.items:
                if not item.all_has_at_least_one_tag(self.forbidden_tags):
                    return True

        return False
