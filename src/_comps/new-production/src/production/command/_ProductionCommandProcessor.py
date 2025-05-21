from abc import ABCMeta, abstractmethod

from ._ProductionCommand import ProductionCommand


class ProductionCommandProcessor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_command(self, command):
        # type: (ProductionCommand) -> None
        raise NotImplementedError()
