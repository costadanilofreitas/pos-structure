from abc import ABCMeta, abstractmethod


class Sleeper(object):
    __meta__ = ABCMeta

    @abstractmethod
    def sleep(self, secs):
        # type: (int) -> None
        raise NotImplementedError()
