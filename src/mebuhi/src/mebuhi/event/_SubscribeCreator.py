from abc import ABCMeta, abstractmethod


class SubscriberCreator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_subscriber(self, subject):
        # type: (str) -> int
        raise NotImplementedError()
