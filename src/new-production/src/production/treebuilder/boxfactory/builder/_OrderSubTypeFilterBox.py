from production.box import OrderSubTypeFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderSubTypeFilterBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(OrderSubTypeFilterBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> OrderSubTypeFilterBox
        return OrderSubTypeFilterBox(config.name,
                                     config.sons,
                                     self.get_extra(config, "AllowedSubTypes", None),
                                     self.get_extra(config, "ForbiddenSubTypes", None),
                                     self.get_logger(config))
