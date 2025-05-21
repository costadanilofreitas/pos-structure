from abc import ABCMeta, abstractmethod

from report.command import Command


class CommandProcessor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_bytes(self, command):
        # type: (Command) -> bytes
        raise NotImplementedError()
