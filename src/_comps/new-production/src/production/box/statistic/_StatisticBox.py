from abc import ABCMeta, abstractmethod
from logging import Logger

from production.model import ProductionOrder, ProdStates
from typing import Optional, Union, List, Callable

from .._ProductionBox import ProductionBox
from ...manager import StatisticUpdater


class StatisticBox(ProductionBox):
    __metaclass__ = ABCMeta

    def __init__(self, name, sons, statistic_updater, logger, get_config):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], StatisticUpdater, Logger, Callable[[str], str]) -> None
        super(StatisticBox, self).__init__(name, sons, logger)
        self.statistic_updater = statistic_updater
        self.statistic_name = get_config("StatisticName")

    def order_modified(self, order):
        # type: (ProductionOrder) -> None
        if order.prod_state != ProdStates.INVALID:
            new_statistic = self.update_statistics(order)
            if new_statistic is not None:
                self.statistic_updater.update_statistics(order.order_id, {self.statistic_name: new_statistic})
                self.debug('statistic "{}" updated to "{}"'.format(self.statistic_name, new_statistic))
        self.send_to_children(order)

    @abstractmethod
    def update_statistics(self, order):
        # type: (ProductionOrder) -> Optional[float]
        raise NotImplementedError()
