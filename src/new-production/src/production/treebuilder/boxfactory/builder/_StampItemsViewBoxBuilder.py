from production.box import StampItemsViewBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class StampItemsViewBoxBuilder(BoxBuilder):
    def __init__(self, order_changer, views, loggers):
        super(StampItemsViewBoxBuilder, self).__init__(loggers)
        self.order_changer = order_changer
        self.views = views
        self.loggers = loggers

    def build(self, config):
        # type: (BoxConfiguration) -> StampItemsViewBox
        return StampItemsViewBox(
            config.name,
            self.order_changer,
            self.views[config.extra_config["View"]],
            config.sons,
            self.get_logger(config)
        )
