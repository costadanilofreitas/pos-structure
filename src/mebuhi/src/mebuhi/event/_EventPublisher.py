from abc import ABCMeta, abstractmethod

from messagebus import Event


class EventPublisher(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def new_event(self, event):
        # type: (Event) -> None
        raise NotImplementedError()
