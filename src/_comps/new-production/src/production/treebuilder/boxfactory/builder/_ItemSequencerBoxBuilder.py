from production.box import ItemSequencerBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ItemSequencerBoxBuilder(BoxBuilder):
    def __init__(self, order_changer, loggers):
        super(ItemSequencerBoxBuilder, self).__init__(loggers)
        self.order_changer = order_changer
        self.loggers = loggers

    def build(self, config):
        # type: (BoxConfiguration) -> ItemSequencerBox
        return ItemSequencerBox(
            config.name,
            self.order_changer,
            config.sons,
            self.get_logger(config)
        )
