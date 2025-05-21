from production.box import CustomPropertyValueFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class CustomPropertyValueFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(CustomPropertyValueFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> CustomPropertyValueFilterBox
        return CustomPropertyValueFilterBox(config.name,
                                            config.sons,
                                            self.get_extra(config, "PropertyName", None),
                                            self.get_extra(config, "AllowedValues", None),
                                            self.get_extra(config, "ExcludedValues", None),
                                            self.get_logger(config))
