from production.box import FromOrderStateFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class FromOrderStateFilterBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(FromOrderStateFilterBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> FromOrderStateFilterBox
        return FromOrderStateFilterBox(config.name,
                                       config.sons,
                                       self.get_extra(config, "OrderStates", None),
                                       self.get_logger(config))
