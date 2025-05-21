from abc import ABCMeta, abstractmethod


class Translator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def translate_words(self, words):
        raise NotImplementedError()
