from old_helper import round_half_away_from_zero
from pos_model import SaleItem, TaxItem
from typing import List, Tuple, Dict, Optional
from msgbus import MBEasyContext, FM_PARAM, TK_SYS_ACK
from bustoken import TK_FISCALWRAPPER_GET_CST, TK_FISCALWRAPPER_GET_BASE_REDUCTION

from _FixedRateTaxCalculator import FixedRateTaxCalculator


class ReducedBaseAmountTaxCalculator(FixedRateTaxCalculator):
    def __init__(self, mbcontext, tax_code, tax_name, tax_index, rate, part_codes, params):
        # type: (MBEasyContext, unicode, unicode, unicode, float, Dict[int, int], unicode) -> None
        super(ReducedBaseAmountTaxCalculator, self).__init__(mbcontext, tax_code, tax_name, tax_index, rate, part_codes, params)
        self.mbcontext = mbcontext
        self.taxes_to_reduce = params.split('|') if params else []
        self.percentage_to_reduce = 0.0
        ret = mbcontext.MB_EasySendMessage("FiscalWrapper", token=TK_FISCALWRAPPER_GET_CST, format=FM_PARAM)
        if ret.token != TK_SYS_ACK:
            raise Exception("Waiting for FiscalWrapper to start")
        else:
            self.cst_dict = eval(ret.data)
        ret = mbcontext.MB_EasySendMessage("FiscalWrapper", token=TK_FISCALWRAPPER_GET_BASE_REDUCTION, format=FM_PARAM)
        if ret.token != TK_SYS_ACK:
            raise Exception("Waiting for FiscalWrapper to start")
        else:
            self.base_reduction_dict = eval(ret.data)

    def calculate_tax(self, sale_item, previous_taxes):
        # type: (SaleItem, List[Tuple[SaleItem, TaxItem]]) -> Optional[TaxItem]
        tax_item = super(ReducedBaseAmountTaxCalculator, self).calculate_tax(sale_item, previous_taxes)
        if tax_item is None:
            return None

        reduced_base_amount = 0.0
        for previous_tax in previous_taxes:
            if previous_tax[1].tax_name in self.taxes_to_reduce:
                reduced_base_amount += previous_tax[1].tax_amount_ad

        self.percentage_to_reduce = 0
        rate = self.rate

        cst_icms = int(self.cst_dict.get((sale_item.part_code, "CST_ICMS")))

        if self.tax_name == "ICMS":
            if cst_icms == 20:
                self.percentage_to_reduce = float(self.base_reduction_dict.get(sale_item.part_code, 0)) / 100
            elif cst_icms == 60:
                rate = 0

        elif self.tax_name in ("PIS", "COFINS") and cst_icms == 40:
            reduced_base_amount = 0

        if self.tax_name == "FCP":
            reduced_base_amount = 0
            if cst_icms != 0:
                self.percentage_to_reduce = float(self.base_reduction_dict.get(sale_item.part_code, 0)) / 100

        tax_item.base_amount_ad = (tax_item.base_amount_ad * (1 - self.percentage_to_reduce)) - reduced_base_amount
        if tax_item.base_amount_ad < 0:
            tax_item.base_amount_ad = 0

        tax_item.tax_amount_bd = round_half_away_from_zero(tax_item.base_amount_bd * rate, 6)
        tax_item.tax_amount_ad = round_half_away_from_zero(tax_item.base_amount_ad * rate, 6)

        return tax_item
