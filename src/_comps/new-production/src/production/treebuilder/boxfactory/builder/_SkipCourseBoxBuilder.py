from production.box import SkipCourseBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class SkipCourseBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(SkipCourseBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> SkipCourseBoxBuilder
        return SkipCourseBox(config.name,
                             config.sons,
                             self.get_extra(config, "SkipPodTypes", []),
                             self.get_extra(config, "SkipSaleTypes", []),
                             self.get_logger(config))
