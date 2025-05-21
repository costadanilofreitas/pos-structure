from abc import ABCMeta, abstractmethod
from mw_helper import BaseRepository


class CurrencyConversionRepository(BaseRepository):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_currency_exchange(self):
        # type: () -> float
        raise NotImplementedError()
