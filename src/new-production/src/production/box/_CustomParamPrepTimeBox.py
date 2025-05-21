from logging import Logger

from production.repository import ProductRepository
from timeutil import Clock
from typing import List, Optional, Union, Any

from ._PrepTimeBox import PrepTimeBox
from ._ProductionBox import ProductionBox


class CustomParamPrepTimeBox(PrepTimeBox):
    def __init__(self, name, sons, product_repository, clock, publish_scheduler=None, wait_even_if_done=False, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], ProductRepository, Clock, Any, bool, Logger) -> None # noqa
        prep_times = product_repository.get_prep_times()
        super(CustomParamPrepTimeBox, self).__init__(name,
                                                     sons,
                                                     prep_times,
                                                     clock,
                                                     publish_scheduler,
                                                     wait_even_if_done,
                                                     logger)
