from logging import Logger

from _OrderChangerProductionBox import OrderChangerProductionBox
from production.box import ProductionBox
from production.repository import ProductRepository
from typing import Optional, Union, List


class MasterPartCodeConverterBox(OrderChangerProductionBox):

    def __init__(self, name, sons, product_repository, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], ProductRepository, Logger) -> None
        super(MasterPartCodeConverterBox, self).__init__(name, sons, logger)
        self.master_product_map = product_repository.get_master_product_map()

    def change_order(self, order):
        for item in order.items:
            if item.part_code in self.master_product_map:
                new_data = self.master_product_map[item.part_code]
                item.original_part_code = item.part_code
                item.original_description = item.description
                item.part_code = new_data[0]
                item.description = new_data[1]

        return order
