from logging import Logger
from typing import Optional, List, Union

from production.treebuilder import ViewConfiguration, BoxConfiguration


def get_extra(config, name, default):
    if name in config.extra_config:
        return config.extra_config[name]
    else:
        return default


def get_logger(config, loggers):
    # type: (Union[ViewConfiguration, BoxConfiguration], List[Logger]) -> Optional[Logger]

    if config.log_level in loggers:
        return loggers[config.log_level]
    else:
        return None
