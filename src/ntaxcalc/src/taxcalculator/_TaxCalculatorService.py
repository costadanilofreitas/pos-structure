from pos_model import OrderParser
from xml.etree import cElementTree as eTree

from _GeneralTaxCalculator import GeneralTaxCalculator
from _OrderFormatter import OrderFormatter


class TaxCalculatorService(object):
    def __init__(self, order_parser, general_tax_calculator, order_formatter):
        # type: (OrderParser, GeneralTaxCalculator, OrderFormatter) -> None
        self.order_parser = order_parser
        self.general_tax_calculator = general_tax_calculator
        self.order_formatter = order_formatter

    def calculate_taxes(self, order_str):
        # type: (str) -> unicode
        xml = eTree.XML(order_str)
        root = xml if xml.tag == "Order" else None
        order_xml = root or xml.find(".//Order")
        if not order_xml:
            raise Exception("Invalid order XML")

        order = self.order_parser.parse_order(order_xml)
        for sale_item in order.sale_items:
            tax_items = self.general_tax_calculator.calculate_all_taxes(sale_item)
            sale_item.taxes = tax_items

        formatted_order = self.order_formatter.format_order(order)

        return formatted_order

    def insert_tx_idx(self, order_str):
        # type: (str) -> unicode
        order_xml = eTree.XML(order_str).find("Order")
        for sale_line in order_xml.findall("SaleLine"):
            if int(sale_line.get("qty") or 1) == 0:
                continue

            sale_item = self.order_parser.create_sale_item(sale_line)
            tax_items = self.general_tax_calculator.calculate_all_taxes(sale_item)

            unit_price = 0 if sale_line.get("unitPrice") is None else float(sale_line.get("unitPrice"))
            added_price = 0 if sale_line.get("addedUnitPrice") is None else float(sale_line.get("addedUnitPrice"))
            sale_line_price = added_price if unit_price == 0 else unit_price

            if tax_items and float(sale_line_price) > 0:
                sale_item.taxes = tax_items
                tax_item = sale_item.get_tax_item("ICMS")
                if tax_item is None:
                    continue

                sale_line.set("taxIndex", tax_item.tax_index)
        return eTree.tostring(order_xml)
