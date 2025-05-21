from logging import Logger

from production.command import ProductionCommandProcessor
from production.manager import OrderChanger
from production.treebuilder import BoxConfiguration
from production.view import ProductionView
from typing import Dict

from production.box import ViewBox


class ViewBoxBuilder(object):
    def __init__(self, command_processor, order_changer, views, loggers):
        # type: (ProductionCommandProcessor, OrderChanger, Dict[str, ProductionView], Dict[str, Logger]) -> None
        self.command_processor = command_processor
        self.order_changer = order_changer
        self.views = views
        self.loggers = loggers

    def build(self, config):
        # type: (BoxConfiguration) -> ViewBox
        if "View" not in config.extra_config:
            raise Exception("View box without a configured View: {}".format(config.name))

        tag_from = "TOTALED" if "TagFrom" not in config.extra_config \
            else config.extra_config["TagFrom"]
        prod_state_from = "TOTALED" if "ProdStateFrom" not in config.extra_config \
            else config.extra_config["ProdStateFrom"]
        return ViewBox(config.name,
                       self.command_processor,
                       self.order_changer,
                       self.views[config.extra_config["View"]],
                       tag_from,
                       prod_state_from,
                       self.loggers[config.log_level])
