from production.box import CFHHiderBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class CFHHiderBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(CFHHiderBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> CFHHiderBox
        return CFHHiderBox(config.name,
                           config.sons,
                           self.product_repository.get_cfh_items(),
                           self.get_logger(config))
