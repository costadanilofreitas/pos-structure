from abc import ABCMeta, abstractmethod

from typing import List  # noqa
from datetime import datetime  # noqa

from _Transfer import Transfer  # noqa


class TransferRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_transfers(self, initial_date, end_date):
        # type: (datetime, datetime) -> List[Transfer]
        raise NotImplementedError()
