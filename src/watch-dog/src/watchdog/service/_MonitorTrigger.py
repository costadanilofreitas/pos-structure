from abc import ABCMeta, abstractmethod

from watchdog.model import Component


class MonitorTrigger(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def fire(self, component):
        # type: (Component) -> None
        raise NotImplementedError()
