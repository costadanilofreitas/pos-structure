from abc import ABCMeta, abstractmethod

from typing import List, Dict  # noqa


class I18nRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def internationalize(self, labels):
        # type: (List[str]) -> Dict[str, str]
        raise NotImplementedError()

    @abstractmethod
    def get_date_format(self):
        # type: () -> str
        raise NotImplementedError()

    @abstractmethod
    def get_date_time_format(self):
        # type: () -> str
        raise NotImplementedError()

    @abstractmethod
    def get_decimal_separator(self):
        # type: () -> str
        raise NotImplementedError()

    @abstractmethod
    def get_thousands_separator(self):
        # type: () -> str
        raise NotImplementedError()

    @abstractmethod
    def get_currency_symbol(self):
        # type: () -> str
        raise NotImplementedError()

    @abstractmethod
    def get_currency_symbol_position(self):
        # type: () -> str
        raise NotImplementedError()

    @abstractmethod
    def get_decimal_places(self):
        # type: () -> str
        raise NotImplementedError()
