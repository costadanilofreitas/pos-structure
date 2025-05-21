from production.box import PodTypeFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class PodTypeFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(PodTypeFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> PodTypeFilterBox
        return PodTypeFilterBox(config.name,
                                config.sons,
                                self.get_extra(config, "AllowedPodTypes", []),
                                self.get_extra(config, "ExcludedPodTypes", []),
                                self.get_logger(config))
