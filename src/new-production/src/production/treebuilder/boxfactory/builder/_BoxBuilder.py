from abc import ABCMeta, abstractmethod
from logging import Logger

from production.treebuilder import BoxConfiguration
from typing import Dict, Optional, Any

from production.box import ProductionBox


class BoxBuilder(object):
    __metaclass__ = ABCMeta

    def __init__(self, loggers):
        # type: (Dict[str, Logger]) -> None
        self.loggers = loggers

    @abstractmethod
    def build(self, config):
        # type: (BoxConfiguration) -> ProductionBox
        raise NotImplementedError()

    def get_extra(self, config, name, default):
        # type: (BoxConfiguration, str, Any) -> Any
        if name in config.extra_config:
            return config.extra_config[name]
        else:
            return default
        
    def get_logger(self, config):
        # type: (BoxConfiguration) -> Optional[Logger]
        if config.log_level in self.loggers:
            return self.loggers[config.log_level]
        else:
            return None
