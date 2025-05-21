from production.box import SaleTypeFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class SaleTypeFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(SaleTypeFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> SaleTypeFilterBox
        return SaleTypeFilterBox(config.name,
                                 config.sons,
                                 self.get_extra(config, "AllowedSaleTypes", None),
                                 self.get_logger(config))
