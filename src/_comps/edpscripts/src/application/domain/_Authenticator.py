from abc import ABCMeta, abstractmethod


class Authenticator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def authenticate(self, username, password):
        # type: (str, str) -> None
        raise NotImplementedError()
