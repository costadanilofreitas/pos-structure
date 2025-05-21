from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class AllItemsDoneBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(AllItemsDoneBox, self).__init__(name, sons, logger)

    def change_order(self, order):
        for item in order.items:
            if not item.all_has_at_least_one_tag(["done", "no-cook"]):
                return None

        return order
