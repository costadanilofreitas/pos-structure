from abc import ABCMeta, abstractmethod


class Cleaner(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def clean_idle_listeners(self):
        # type: () -> None
        raise NotImplementedError()
