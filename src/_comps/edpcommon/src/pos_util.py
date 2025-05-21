from typing import List
from xml.etree import ElementTree
from pos_model import TaxItem
from xml.sax.saxutils import escape


class SaleLineUtil(object):
    def __init__(self):
        pass

    def get_product_name_from_tax_item(self, tax_item, sale_lines):
        # type: (TaxItem, List[ElementTree]) -> unicode
        sale_line = self._get_sale_line_by_tax_item(tax_item, sale_lines)

        if sale_line is None:
            raise Exception("SaleLine not found for product: {0}.{1}".format(tax_item.item_id, tax_item.part_code))

        product_name = escape(sale_line.get("productName"))

        return product_name

    def get_sale_line_by_tax_item(self, tax_item, sale_lines):
        # type: (TaxItem, List[ElementTree]) -> Optional[ElementTree]
        for sale_line in sale_lines:
            if sale_line.get("itemId") == tax_item.item_id and int(sale_line.get("partCode")) == tax_item.part_code:
                return sale_line

        raise Exception("SaleLine not found for product: {0}.{1}".format(tax_item.item_id, tax_item.part_code))
