from ._OrderChangerProductionBox import OrderChangerProductionBox


class RemoveDeletedItemsBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(RemoveDeletedItemsBox, self).__init__(name, sons, logger)

    def change_order(self, order):
        order.items = self.remove_deleted_items(order.items)
        return order

    def remove_deleted_items(self, items):
        new_items = []
        for item in items:
            if item.qty > 0:
                new_items.append(item)
        return new_items
