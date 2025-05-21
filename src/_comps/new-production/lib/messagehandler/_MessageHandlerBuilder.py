from abc import ABCMeta, abstractmethod
from ._MessageHandler import MessageHandler


class MessageHandlerBuilder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_singletons(self):
        # type: () -> None
        """
        This method is called once when the component is initialing. All singletons of the component must be
        created on this method
        """
        raise NotImplementedError()

    @abstractmethod
    def build_message_handler(self):
        # type: () -> MessageHandler
        """
        This method is called once per message that must be handled. This method must return an instance of EventHandler
        that will be used to handle the received message
        Any object that must be created per request must be created on this method and associated with the EventHandler
        :return: an instance of MessageHandler that will be used to handle the received message
        """
        raise NotImplementedError()

    @abstractmethod
    def destroy_message_handler(self, message_handler):
        # type: (MessageHandler) -> None
        """
        This method will be called after the received message is called and the MessageHandler is no long necessary.
        Any object that needs special handling for destruction must be handled in this method
        :param message_handler: the instance of the EventHandler that is no longer necessary
        """
        raise NotImplementedError()

    @abstractmethod
    def destroy_singletons(self):
        # type: () -> None
        """
        This method is called once when the component is finalizing. Any singleton that needs special handling for
        destruction must be handled here
        """
        raise NotImplementedError()
