import sys
from abc import ABCMeta
from logging import Logger

from production.box.statistic import StatisticBox
from production.manager import StatisticUpdater
from production.treebuilder import BoxConfiguration
from typing import Dict

from ._BoxBuilder import BoxBuilder


class StatisticBoxBuilder(BoxBuilder):
    __metaclass__ = ABCMeta

    def __init__(self, statistic_updater, loggers):
        # type: (StatisticUpdater, Dict[str, Logger]) -> None
        super(StatisticBoxBuilder, self).__init__(loggers)
        self.statistic_updater = statistic_updater

    def build(self, config):
        # type: (BoxConfiguration) -> StatisticBox

        def get_config(config_name):
            return self.get_extra_config(config, config_name)

        self.loggers['DEBUG'].info('creating statistic box...')
        statistic_class_name = self.get_extra_config(config, "StatisticClass")

        statistic_type = getattr(sys.modules["production.box.statistic"], statistic_class_name, None)
        if statistic_type is None:
            self.loggers['DEBUG'].info("StatisticClass ({}) does not exist".format(statistic_class_name))
            raise Exception("StatisticClass ({}) does not exist".format(statistic_class_name))

        self.loggers['DEBUG'].info('StatisticClass = {}'.format(statistic_class_name))
        self.loggers['DEBUG'].info('StatisticType = {}'.format(statistic_type))
        return statistic_type(config.name, config.sons, self.statistic_updater, self.get_logger(config),
                              get_config)

    def get_extra_config(self, config, config_name):
        config_value = self.get_extra(config, config_name, None)
        if config_value is None:
            self.loggers['DEBUG'].info("({}) does not exist".format(config_name))
            raise Exception("({}) does not exist".format(config_name))

        return config_value
