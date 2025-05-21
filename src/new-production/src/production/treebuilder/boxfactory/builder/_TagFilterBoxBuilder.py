from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder
from production.box import TagFilterBox


class TagFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(TagFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> TagFilterBox
        return TagFilterBox(config.name,
                            config.sons,
                            self.get_extra(config, "AllowedTags", None),
                            self.get_extra(config, "ForbiddenTags", None),
                            self.get_extra(config, "AllowComboTags", 'False'),
                            self.get_logger(config))
