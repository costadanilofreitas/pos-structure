from old_helper import BaseRepository
from msgbus import MBEasyContext
from persistence import Connection
from typing import Dict, Tuple


class FiscalParameterRepository(BaseRepository):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        super(FiscalParameterRepository, self).__init__(mbcontext)

    def get_fiscal_parameters(self, loader_params):
        def inner_func(conn):
            # type: (Connection) -> Dict[Tuple[int, unicode], unicode]
            query = "select ProductCode, ParamName, ParamValue from FiscalParameter"
            return {(int(x.get_entry(0)), x.get_entry(1)): x.get_entry(2) for x in conn.select(query)}

        fiscal_params = self.execute_with_connection(inner_func, service_name="FiscalPersistence")

        if loader_params:
            for product in loader_params:
                product_code = product['PRODUCT_CODE']
                for param in product:
                    if param == 'PRODUCT_CODE':
                        continue
                    result = {(int(product_code), str(param)): str(product[param])}
                    fiscal_params.update(result)

        return fiscal_params
