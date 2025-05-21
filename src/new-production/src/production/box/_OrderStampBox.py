from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class OrderStampBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(OrderStampBox, self).__init__(name, sons, logger)

    def change_order(self, order):
        order.stamped = True
        for item in order.items:
            item.stamped = True
        return order
