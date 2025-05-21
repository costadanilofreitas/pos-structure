from abc import ABCMeta, abstractmethod

from domain import Session


class SessionRetriever(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_session(self, id):
        # type: (str) -> Session
        raise NotImplementedError()
