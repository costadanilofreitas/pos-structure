from logging import Logger

from production.repository import ProductRepository
from typing import Union, List

from ._ComboFilterBox import ComboFilterBox
from ._ProductionBox import ProductionBox


class ShowOnJitComboFilterBox(ComboFilterBox):
    def __init__(self, name, sons, product_repository, logger=None):
        # type: (str, Union[ProductionBox, List[ProductionBox]], ProductRepository, Logger) -> None
        items_to_keep = product_repository.get_combos_to_keep()
        super(ShowOnJitComboFilterBox, self).__init__(name, sons, items_to_keep, logger)
