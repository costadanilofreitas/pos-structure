from random import getrandbits

from production.command import ProductionCommand


class PurgeOrdersCommand(ProductionCommand):
    def __init__(self, orders):
        super(PurgeOrdersCommand, self).__init__(None, None)
        self.orders = orders

    def get_hash_extra_value(self):
        return "PurgeOrdersCommand{}".format(getrandbits(40))
