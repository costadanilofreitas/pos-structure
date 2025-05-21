from production.box import OrderMergerBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderMergerBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(OrderMergerBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> OrderMergerBox
        return OrderMergerBox(config.name,
                              config.sons,
                              self.get_logger(config))
