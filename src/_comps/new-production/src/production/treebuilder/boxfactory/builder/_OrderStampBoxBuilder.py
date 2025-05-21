from production.box import OrderStampBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderStampBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(OrderStampBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> OrderStampBox
        return OrderStampBox(config.name,
                             config.sons,
                             self.get_logger(config))
