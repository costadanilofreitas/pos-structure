from _EscPosFormatter import EscPosFormatter
from escposformatter import CommandFactory
from escposformatter.processor import AlignCommandProcessor, BoldCommandProcessor, RepeatCommandProcessor, \
    FontCommandProcessor, NewLineCommandProcessor
from report.command import AlignCommand, BoldCommand, RepeatCommand, FontCommand, NewLineCommand


class DefaultEscPosFormatter(EscPosFormatter):
    def __init__(self, encoding="cp860"):
        commands = {
            FontCommand: FontCommandProcessor(),
            AlignCommand: AlignCommandProcessor(),
            BoldCommand: BoldCommandProcessor(),
            RepeatCommand: RepeatCommandProcessor(),
            NewLineCommand: NewLineCommandProcessor()
        }
        super(DefaultEscPosFormatter, self).__init__(encoding,
                                                     DefaultEscPosFormatter.DefaultCommandFactory(commands))

    class DefaultCommandFactory(CommandFactory):
        def __init__(self, commands):
            self.commands = commands

        def get_processor(self, command):
            return self.commands[type(command)]
