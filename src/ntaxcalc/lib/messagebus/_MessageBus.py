from abc import ABCMeta, abstractmethod

from ._Message import Message
from ._Event import Event


class MessageBus(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def publish_event(self, event):
        # type: (Event) -> Message
        raise NotImplementedError()

    @abstractmethod
    def send_message(self, component, message):
        # type: (unicode, Message) -> Message
        raise NotImplementedError()

    @abstractmethod
    def subscribe(self, subject):
        # type: (unicode) -> None
        raise NotImplementedError()

    @abstractmethod
    def reply_message(self, message, reply_message):
        # type: (Message, Message) -> None
        raise NotImplementedError()

    @abstractmethod
    def reply_event(self, event, reply_message):
        # type: (Event, Message) -> None
        raise NotImplementedError()
