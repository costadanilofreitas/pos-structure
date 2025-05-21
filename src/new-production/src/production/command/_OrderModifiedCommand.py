from random import getrandbits

from production.command import ProductionCommand


class OrderModifiedCommand(ProductionCommand):
    def __init__(self, order_id, order):
        super(OrderModifiedCommand, self).__init__(order_id, None)
        self.order = order

    def get_hash_extra_value(self):
        # type: () -> str
        return "OrderModifiedCommand{}".format(getrandbits(40))
