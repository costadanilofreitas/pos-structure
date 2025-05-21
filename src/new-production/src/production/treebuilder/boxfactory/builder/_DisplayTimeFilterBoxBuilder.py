from production.box import DisplayTimeFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class DisplayTimeFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(DisplayTimeFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> DisplayTimeFilterBox
        return DisplayTimeFilterBox(config.name,
                                    config.sons,
                                    self.get_extra(config, "ExpirationTime", None),
                                    self.get_logger(config))
