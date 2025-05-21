from production.box import HideOptionBox, OrderStateTimerBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderStateTimerBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(OrderStateTimerBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> OrderStateTimerBox
        return OrderStateTimerBox(config.name,
                                  config.sons,
                                  self.get_extra(config, "OrderState", []),
                                  self.get_logger(config))
