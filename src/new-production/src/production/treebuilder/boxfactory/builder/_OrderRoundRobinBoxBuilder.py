from production.box import OrderRoundRobinBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderRoundRobinBoxBuilder(BoxBuilder):
    def __init__(self, order_changer, loggers):
        super(OrderRoundRobinBoxBuilder, self).__init__(loggers)
        self.order_changer = order_changer

    def build(self, config):
        # type: (BoxConfiguration) -> OrderRoundRobinBox
        return OrderRoundRobinBox(config.name,
                                  config.sons,
                                  self.order_changer,
                                  self.get_extra(config, "Paths", None),
                                  self.get_logger(config))
