from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class AllServedItemsBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(AllServedItemsBox, self).__init__(name, sons, logger)

    def change_order(self, order):

        for item in order.items:
            if not item.all_has_at_least_one_tag(["served"]):
                return None

        return order
