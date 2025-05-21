from production.box import CustomPropertyFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class CustomPropertyFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(CustomPropertyFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> CustomPropertyFilterBox
        return CustomPropertyFilterBox(config.name,
                                       config.sons,
                                       self.get_extra(config, "AllowedPropertyNames", None),
                                       self.get_extra(config, "ForbiddenPropertyNames", None),
                                       self.get_logger(config))
