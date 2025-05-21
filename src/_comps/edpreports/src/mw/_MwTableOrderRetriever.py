import json
from datetime import datetime

from domain import TableOrderRetriever, TableOrderSaleLine, TableService, TableOrder, Table
from xml.etree import cElementTree as eTree
from sysactions import get_user_information

from typing import List  # noqa


class MwTableOrderRetriever(TableOrderRetriever):
    def __init__(self, table_service):
        # type: (TableService) -> None
        self.table_service = table_service

    def get_table_order(self, pos_id, table_id):
        # type: (str, str) -> Table
        xml_table_picture = self.table_service.get_table_picture(pos_id, table_id)

        xml = eTree.XML(xml_table_picture)
        table = Table()

        table_xml = xml.find(".")
        table.table_id = table_xml.attrib["id"]
        table.total_amount = float(table_xml.attrib["totalAmount"]) if "totalAmount" in table_xml.attrib else 0.0
        table.service_seats = int(table_xml.attrib["serviceSeats"]) if "serviceSeats" in table_xml.attrib else 0
        table.total_per_seat = float(table_xml.attrib["totalPerSeat"]) if "totalPerSeat" in table_xml.attrib else 0.0
        table.total_discounts = float(table_xml.attrib["discountAmount"]) if "discountAmount" in table_xml.attrib else 0.0
        tip_rate = self.table_service.get_tip_rate()
        default_tip_amount = (table.total_amount * tip_rate) / 100 if tip_rate else 0.0
        table.tip = float(table_xml.get("tip") if table_xml.get("tip") is not None else default_tip_amount)
        table.start_date = datetime.strptime(table_xml.attrib["startTS"], "%Y-%m-%d %H:%M:%S") if "startTS" in table_xml.attrib else None
        table.user_id = table_xml.attrib["userId"] if "userId" in table_xml.attrib else ""
        user_information = eTree.XML(get_user_information(table.user_id)).find("user")
        table.user_name = user_information.get("LongName")

        table_order_total_gross = 0.0
        total_discount_amount = 0.0
        total_tip = 0.0

        for order_xml in xml.findall("Orders/Order"):
            total_order_amount = float(order_xml.get("totalAmount"))
            total_order_after_discount = order_xml.get("totalAfterDiscount")
            order_discount_amount = order_xml.get("discountAmount")
            order_state = order_xml.get("state")
            default_order_tip_amount = (float(order_xml.get("totalGross")) * tip_rate) / 100 if tip_rate else 0.0
            if order_state != "TOTALED":
                tip = default_order_tip_amount
            else:
                tip = float(order_xml.get("tip"))
            total_tip += tip
            table_order_total_gross += float(order_xml.get("totalGross"))
            total_discount_amount += float(order_discount_amount)
            total_order_tender = order_xml.get("totalTender")
            order_state = order_xml.get("state")
            order_id = order_xml.get("orderId")
            custom_order_properties = order_xml.findall("CustomOrderProperties/OrderProperty")

            split_key = "1"
            for custom_property in custom_order_properties:
                properties = custom_property.find(".")
                if "key" in properties.attrib and properties.attrib["key"] == "SPLIT_KEY":
                    split_key = properties.attrib["value"]
                    break

            sale_lines = self._extract_sales_lines(order_xml.findall("SaleLine"), table.service_seats)

            order = TableOrder(order_id, order_state, total_order_amount, total_order_after_discount,
                               total_order_tender, order_discount_amount, sale_lines, split_key, tip)
            table.orders.append(order)

        table.sub_total_amount = table_order_total_gross + total_discount_amount
        table.tip = total_tip
        table.total_amount = table_order_total_gross + table.tip

        return table

    @staticmethod
    def _extract_sales_lines(order_sales, service_seats):
        # type: (List[eTree.Element], int) -> List[TableOrderSaleLine]
        deleted_line_numbers = map(lambda x: x.get("lineNumber"),
                                   filter(lambda x: x.get("level") == "0" and x.get("qty") == "0", order_sales))
        active_sale_lines = filter(lambda x: x.get("lineNumber") not in deleted_line_numbers, order_sales)

        sales_line = []  # type: List[TableOrderSaleLine]

        last_seat = None
        for sale_line in active_sale_lines:
            products = sale_line.get("productName")
            price = float(sale_line.get("itemPrice") or 0)
            qty = float(sale_line.get("qty") or 0)
            default_qty = int(sale_line.get("defaultQty")) if "defaultQty" in sale_line.attrib else 0
            item_type = sale_line.get("itemType")
            level = int(sale_line.get("level") or 0)
            line_number = int(sale_line.get("lineNumber") or 0)
            comment = sale_line.find("Comment")
            if comment is not None:
                comment = comment.get("comment")

            props = sale_line.get("customProperties")
            if props and 'seat' in json.loads(props):
                seat = int(json.loads(props)['seat'])
                seat = 0 if seat > service_seats else seat
                last_seat = seat
            else:
                seat = last_seat if last_seat else 0

            sale_line = TableOrderSaleLine(products, price, qty, default_qty, item_type, seat, level, comment, line_number)

            sales_line.append(sale_line)

        return sales_line
