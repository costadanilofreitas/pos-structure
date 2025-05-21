from production.box import HideOptionBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class HideOptionBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(HideOptionBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> HideOptionBox
        return HideOptionBox(config.name,
                             config.sons,
                             self.get_extra(config, "FixDefaultQuantity", "false").lower() == "true",
                             self.get_logger(config))
