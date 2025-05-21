from production.model import ReportNameNotFoundException, PrinterNameFoundException
from production.treebuilder import ViewConfiguration
from ._CommonViewBuilder import get_extra, get_logger

from production.view import PrinterView


class PrinterViewBuilder(object):
    def __init__(self, message_bus, loggers):
        self.message_bus = message_bus
        self.loggers = loggers

    def build(self, config):
        # type: (ViewConfiguration) -> PrinterView

        if "ReportName" not in config.extra_config:
            raise ReportNameNotFoundException("PrinterView without report: {}".format(config.name))

        if "PrinterName" not in config.extra_config:
            raise PrinterNameFoundException("PrinterView without printer: {}".format(config.name))

        return PrinterView(config.name,
                           self.message_bus,
                           config.extra_config["ReportName"].encode("utf-8"),
                           config.extra_config["PrinterName"].encode("utf-8"),
                           int(get_extra(config, "Timeout", 10000)) * 1000,
                           get_extra(config, "TagOnPrint", "printed").split(";"),
                           get_logger(config, self.loggers))
