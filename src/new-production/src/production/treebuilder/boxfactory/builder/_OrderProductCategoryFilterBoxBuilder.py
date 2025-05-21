from production.box import OrderProductCategoryFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class OrderProductCategoryFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(OrderProductCategoryFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> OrderProductCategoryFilterBox
        return OrderProductCategoryFilterBox(config.name,
                                             config.sons,
                                             self.get_extra(config, "AllowedCategory", None),
                                             self.get_extra(config, "ForbiddenCategory", None),
                                             self.get_extra(config, "FilterMethod", "any"),
                                             self.get_logger(config))
