from production.box import CustomParamPointerBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class CustomParamPointerBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(CustomParamPointerBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> CustomParamPointerBox
        return CustomParamPointerBox(config.name,
                                     config.sons,
                                     self.product_repository,
                                     int(self.get_extra(config, u"DefaultPoints", 0)),
                                     self.get_extra(config, u"CountMergedItems", "true").lower() == "true",
                                     self.get_logger(config))
