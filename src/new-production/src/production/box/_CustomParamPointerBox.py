from logging import Logger

from production.repository import ProductRepository
from typing import List, Optional, Union

from ._PointerBox import PointerBox
from ._ProductionBox import ProductionBox


class CustomParamPointerBox(PointerBox):
    def __init__(self, name, sons, product_repository, default_points, count_merged_items, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], ProductRepository, int, bool, Logger) -> None
        product_points = product_repository.get_product_points()
        super(CustomParamPointerBox, self).__init__(name,
                                                    sons,
                                                    product_points,
                                                    default_points,
                                                    count_merged_items,
                                                    logger)
