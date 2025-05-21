from production.box import ShowOnKitchenFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ShowOnKitchenFilterBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(ShowOnKitchenFilterBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> ShowOnKitchenFilterBox
        return ShowOnKitchenFilterBox(config.name,
                                      config.sons,
                                      self.product_repository,
                                      self.get_extra(config, "ShowAllItems", "False"),
                                      self.get_logger(config))
