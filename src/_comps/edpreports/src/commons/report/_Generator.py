from abc import ABCMeta, abstractmethod


class Generator(object):
    _metaclass__ = ABCMeta

    @abstractmethod
    def generate_data(self):
        raise NotImplementedError()
