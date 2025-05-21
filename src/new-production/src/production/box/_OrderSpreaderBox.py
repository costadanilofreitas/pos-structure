from production.box import ProductionBox


class OrderSpreaderBox(ProductionBox):
    def __init__(self, name, sons, logger=None):
        super(OrderSpreaderBox, self).__init__(name, sons, logger)

    def order_modified(self, order):
        for son in self.sons:
            son.order_modified(order.clone())
