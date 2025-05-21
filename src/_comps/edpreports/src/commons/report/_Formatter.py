from abc import ABCMeta, abstractmethod


class Formatter(object):
    _metaclass__ = ABCMeta

    @abstractmethod
    def format_report(self):
        raise NotImplementedError()
