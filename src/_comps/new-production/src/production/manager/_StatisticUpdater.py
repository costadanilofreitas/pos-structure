from abc import ABCMeta, abstractmethod
from typing import Dict, Any


class StatisticUpdater(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update_statistics(self, order_id, stats):
        # type: (int, Dict[str, Any]) -> None
        raise NotImplementedError()
