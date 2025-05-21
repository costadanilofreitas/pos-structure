from production.box import ProductCodeFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ProductCodeFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(ProductCodeFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> FromOrderStateFilterBox
        return ProductCodeFilterBox(config.name,
                                    config.sons,
                                    self.get_extra(config, "ProductCodes", None),
                                    self.get_extra(config, "KeepChildren", False),
                                    self.get_logger(config))
