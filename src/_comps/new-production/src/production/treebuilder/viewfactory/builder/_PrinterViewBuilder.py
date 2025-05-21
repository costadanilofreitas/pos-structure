from logging import Logger

from production.treebuilder import ViewConfiguration
from typing import Optional

from production.view import PrinterView


class PrinterViewBuilder(object):
    def __init__(self, message_bus, loggers):
        self.message_bus = message_bus
        self.loggers = loggers

    def build(self, config):
        # type: (ViewConfiguration) -> PrinterView
        if "ReportName" not in config.extra_config:
            raise Exception("PrinterView without report: {}".format(config.name))

        if "PrinterName" not in config.extra_config:
            raise Exception("PrinterView without printer: {}".format(config.name))

        return PrinterView(config.name,
                           self.message_bus,
                           config.extra_config["ReportName"].encode("utf-8"),
                           config.extra_config["PrinterName"].encode("utf-8"),
                           int(self.get_extra(config, "Timeout", 10000)) * 1000,
                           self.get_extra(config, "TagOnPrint", "printed").split(";"),
                           self.get_logger(config))

    def get_extra(self, config, name, default):
        if name in config.extra_config:
            return config.extra_config[name]
        else:
            return default

    def get_logger(self, config):
        # type: (ViewConfiguration) -> Optional[Logger]
        if config.log_level in self.loggers:
            return self.loggers[config.log_level]
        else:
            return None
