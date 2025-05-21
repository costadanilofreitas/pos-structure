from mw_helper import ensure_iterable
from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class AllItemHasAtLeastOneTagFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, tags, logger=None):
        super(AllItemHasAtLeastOneTagFilterBox, self).__init__(name, sons, logger)
        self.tags = ensure_iterable(tags)

    def change_order(self, order):
        new_items = []
        for item in order.items:
            if item.all_has_at_least_one_tag(self.tags):
                new_items.append(item)

        order.items = new_items
        return order
