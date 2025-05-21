from msgbus import MBEasyContext
from old_helper import BaseRepository
from typing import List
from persistence import Connection


class ProductRepository(BaseRepository):
    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        super(ProductRepository, self).__init__(mb_context)

    def get_products_with_not_charge_tip(self):
        # type: () -> List[int]
        def inner_func(conn):
            # type: (Connection) -> List[int]
            return [int(x.get_entry(0)) for x in conn.select(self._GetProductsWithNotChargeTip)]

        return self.execute_with_connection(inner_func)

    _GetProductsWithNotChargeTip = \
        """SELECT ProductCode
           FROM ProductCustomParams
           WHERE CustomParamId = 'NotChargeTip' AND CustomParamValue = 'True'
        """
