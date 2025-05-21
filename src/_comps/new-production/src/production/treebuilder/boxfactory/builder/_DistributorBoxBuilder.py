from production.box import DistributorBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class DistributorBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(DistributorBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> DistributorBox
        return DistributorBox(config.name,
                              config.extra_config["Paths"],
                              self.get_logger(config))
