from abc import ABCMeta, abstractmethod

from report.command import Command
from ._CommandProcessor import CommandProcessor  # noqa


class CommandFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_processor(self, command):
        # type: (Command) -> CommandProcessor
        raise NotImplementedError()
