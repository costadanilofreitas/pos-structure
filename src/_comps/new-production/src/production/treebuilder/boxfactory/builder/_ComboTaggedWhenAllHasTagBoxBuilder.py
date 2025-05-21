from production.box import ComboTaggedWhenAllHasTagBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ComboTaggedWhenAllHasTagBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(ComboTaggedWhenAllHasTagBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> ComboTaggedWhenAllHasTagBox
        
        return ComboTaggedWhenAllHasTagBox(config.name,
                                           config.sons,
                                           self.get_extra(config, "Tags", ""),
                                           self.get_extra(config, "TagToAdd", []),
                                           self.get_logger(config))
