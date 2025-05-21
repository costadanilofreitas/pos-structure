from random import getrandbits

from production.command import ProductionCommand


class PublishOrderCommand(ProductionCommand):
    def __init__(self, order_id, order):
        super(PublishOrderCommand, self).__init__(order_id, None)
        self.order = order

    def get_hash_extra_value(self):
        return "PublishOrderCommand{}".format(getrandbits(40))
