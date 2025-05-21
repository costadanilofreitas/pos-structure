from pos_model import Tax
from old_helper import BaseRepository
from msgbus import MBEasyContext
from persistence import Connection


class NTaxCalcRepository(BaseRepository):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        super(NTaxCalcRepository, self).__init__(mbcontext)

    def load_all_taxes(self):
        # type: () -> List[Tax]
        def inner_func(conn):
            # type: (Connection) -> List[Tax]
            taxes = [Tax(x.get_entry(0), x.get_entry(1), float(x.get_entry(2)), x.get_entry(3), x.get_entry(4), x.get_entry(5)) for x in conn.select("SELECT Code, Name, Rate, FiscalIndex, TaxProcessor, Parameters from Tax Order by TaxOrder")]

            return taxes

        return self.execute_with_connection(inner_func, service_name="FiscalPersistence")

    def load_all_products_from_tax(self, tax_code):
        # type: (unicode) -> List[unicode]
        def inner_func(conn):
            # type: (Connection) -> Dict[unicode, unicode]
            products = {int(x.get_entry(0)): int(x.get_entry(0)) for x in conn.select("SELECT ProductCode from ProductTax where TaxCode = '{0}'".format(tax_code))}

            return products

        return self.execute_with_connection(inner_func, service_name="FiscalPersistence")
