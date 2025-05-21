from production.box import OrderSpreaderBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderSpreaderBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(OrderSpreaderBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> OrderSpreaderBox
        return OrderSpreaderBox(config.name,
                                config.sons,
                                self.get_logger(config))
