from production.box import HideOptionBox, ItemPropertiesFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ItemPropertiesFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(ItemPropertiesFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> ItemPropertiesFilterBox
        return ItemPropertiesFilterBox(config.name,
                                       config.sons,
                                       self.get_extra(config, "AllowedProperties", None),
                                       self.get_extra(config, "ForbiddenProperties", None),
                                       self.get_extra(config, "AllowComboProperties", 'False'),
                                       self.get_logger(config))
