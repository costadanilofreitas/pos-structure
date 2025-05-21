from production.box import OrderStateFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderStateFilterBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(OrderStateFilterBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> OrderStateFilterBox
        return OrderStateFilterBox(config.name,
                                   config.sons,
                                   self.get_extra(config, "AllowedOrderStates", []),
                                   self.get_extra(config, "ExcludedOrderStates", []),
                                   self.get_logger(config))
