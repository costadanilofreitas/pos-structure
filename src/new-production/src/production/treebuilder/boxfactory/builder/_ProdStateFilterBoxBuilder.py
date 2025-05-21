from production.box import ProdStateFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ProdStateFilterBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(ProdStateFilterBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> ProdStateFilterBox
        return ProdStateFilterBox(config.name,
                                  config.sons,
                                  self.get_extra(config, "AllowedProdStates", []),
                                  self.get_extra(config, "ExcludedProdStates", []),
                                  self.get_logger(config))
