from pos_model import SaleItem, TaxItem
from typing import List

from _TaxCalculator import TaxCalculator


class GeneralTaxCalculator(object):
    def __init__(self, tax_calculators):
        # type: (List[TaxCalculator]) -> None
        self.tax_calculators = tax_calculators

    def calculate_all_taxes(self, sale_item):
        # type: (SaleItem) -> List[TaxItem]
        previous_taxes = []
        for tax_calculator in self.tax_calculators:
            tax_item = tax_calculator.calculate_tax(sale_item, previous_taxes)
            if tax_item is not None:
                previous_taxes.append((sale_item, tax_item))

        calculates_taxes = []
        for tax_tuple in previous_taxes:
            calculates_taxes.append(tax_tuple[1])

        return calculates_taxes
