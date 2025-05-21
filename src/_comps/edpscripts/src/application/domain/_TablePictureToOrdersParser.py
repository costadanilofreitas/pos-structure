from application.domain import Order, CustomOrderProperty
from typing import List  # noqa
from xml.etree import cElementTree as eTree


class TablePictureToOrdersParser(object):
    @staticmethod
    def parse(table_picture):
        # type: (str) -> List[Order]
        xml_table_picture = eTree.XML(table_picture)
        xml_orders = xml_table_picture.findall("Orders/Order")
        result_orders = []
        for order in xml_orders:
            order_custom_property_list = []
            for order_custom_property in order.findall("CustomOrderProperties/OrderProperty"):
                order_custom_property_list.append(
                    CustomOrderProperty(order_custom_property.get("key"), order_custom_property.get("value")))

            result_orders.append(Order(
                order.get("orderId"),
                float(order.get("totalGross")) + float(order.get("discountAmount")),
                float(order.get("tip")),
                order.get("posId"),
                order_custom_property_list,
                float(order.get("dueAmount"))
            ))

        return result_orders
