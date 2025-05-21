from abc import ABCMeta, abstractmethod
from messagebus import Event, Message, MessageBus


class MessageHandler(object):
    """
    The methods of this class will be called whenever a new message arrives from the message bus that must be
    handled by the component
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_event(self, message_bus, event):
        # type: (MessageBus, Event) -> None
        """
        This method will be called when the component receives an Event (Async or Sync). Every Sync events must be
        replied
        :param message_bus: the instance of the MessageBus that can be used to send messages to other components
        or replying the received message
        :param event: the event that must be handled by the component
        """
        raise NotImplementedError()

    def handle_message(self, message_bus, message):
        # type: (MessageBus, Message) -> None
        """
        This method will be called whenever the components received a Message. Every message must be replied.
        :param message_bus: the instance of the MessageBus that can be used to send messages to other components
        or replying the received message
        :param message: the message that must be handled bt the component
        :return:
        """
        raise NotImplementedError()
