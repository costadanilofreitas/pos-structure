from production.model import CommandNotFoundException
from production.treebuilder import ViewConfiguration
from ._CommonViewBuilder import get_logger
from production.view import CommandView


class CommandViewBuilder(object):
    def __init__(self, command_processor, loggers):
        self.command_processor = command_processor
        self.loggers = loggers

    def build(self, config):
        # type: (ViewConfiguration) -> CommandView

        if "Command" not in config.extra_config:
            raise CommandNotFoundException("CommandView without command: {}".format(config.name))

        command = config.extra_config.get("Command", "")
        return CommandView(config.name, self.command_processor, command, get_logger(config, self.loggers))
