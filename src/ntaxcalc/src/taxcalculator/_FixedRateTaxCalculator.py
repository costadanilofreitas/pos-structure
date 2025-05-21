from old_helper import round_half_away_from_zero
from pos_model import SaleItem, TaxItem
from typing import List, Tuple, Dict, Optional
from msgbus import MBEasyContext

from _TaxCalculator import TaxCalculator


class FixedRateTaxCalculator(TaxCalculator):
    def __init__(self, mbcontext, tax_code, tax_name, tax_index, rate, part_codes, params):
        # type: (MBEasyContext, unicode, unicode, unicode, float, Dict[int, int]) -> None
        self.mbcontext = mbcontext
        import zlib
        self.tax_code = abs(zlib.crc32(tax_code))
        self.tax_name = tax_name
        self.tax_index = tax_index
        self.rate = round_half_away_from_zero(rate / 100, 4)
        self.part_codes = part_codes
        self.params = params

    def calculate_tax(self, sale_item, previous_taxes):
        # type: (SaleItem, List[Tuple[SaleItem, TaxItem]]) -> Optional[TaxItem]
        if sale_item is None:
            raise Exception("cannot be called with sale_item")

        if sale_item.part_code not in self.part_codes:
            return None

        ret_value = self.create_base_tax_item(sale_item)

        ret_value.tax_rate = self.rate
        ret_value.tax_index = self.tax_index
        ret_value.tax_name = self.tax_name
        ret_value.tax_code = self.tax_code
        ret_value.tax_rule_id = self.tax_code
        ret_value.tax_included = 1
        ret_value.base_amount_bd = sale_item.item_price / sale_item.fix_qty_rate
        ret_value.base_amount_ad = (sale_item.item_price - sale_item.item_discount) / sale_item.fix_qty_rate
        ret_value.tax_amount_bd = round_half_away_from_zero(ret_value.base_amount_bd * self.rate, 6)
        ret_value.tax_amount_ad = round_half_away_from_zero(ret_value.base_amount_ad * self.rate, 6)

        return ret_value
