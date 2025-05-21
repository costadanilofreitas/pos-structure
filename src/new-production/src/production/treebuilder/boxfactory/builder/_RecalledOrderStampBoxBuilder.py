from production.box import RecalledOrderStampBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class RecalledOrderStampBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(RecalledOrderStampBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> RecalledOrderStampBoxBuilder
        filter_tag = config.extra_config["FilterTag"] if "FilterTag" in config.extra_config else "done"

        return RecalledOrderStampBox(config.name,
                                     config.sons,
                                     filter_tag,
                                     self.get_logger(config))
