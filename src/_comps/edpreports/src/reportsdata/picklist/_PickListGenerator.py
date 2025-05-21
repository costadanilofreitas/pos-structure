import sys
from msgbus import MBEasyContext  # noqa
from xml.etree import cElementTree as etree
from xml.etree.ElementTree import Element  # noqa
from domain import Clock  # noqa

from commons.report import Generator
from reports_app.picklist.dto import PickListBodyDto
from reports_app.picklist.dto import PickListDto
from reports_app.picklist.dto import PickListHeaderDto
from reports_app.picklist.dto import PickListItem


class PickListGenerator(Generator):
    def __init__(self, mb_context, pick_list_xml, clock, store_number):
        super(PickListGenerator, self).__init__()
        # type: (MBEasyContext, Clock, unicode, unicode) -> None
        self.mb_context = mb_context
        self.clock = clock
        self.store_number = store_number
        self.pick_list_xml = pick_list_xml

    def generate_data(self):
        # type: () -> PickListDto
        order, pod_type, sale_type, pos_id = self._validate_xml_and_get_data()
        pick_list_header = self._generate_header(order)
        pick_list_body = PickListBodyDto(self._generate_body(order))
        return PickListDto(pick_list_header, pick_list_body, pod_type, sale_type, pos_id)

    def _validate_xml_and_get_data(self):
        order = self._validate_xml_and_get_order()
        pod_type = self._validate_pod_type(order)
        pos_id = self._validate_pos_id(order)
        sale_type = self._validate_sale_type(order)
        return order, pod_type, sale_type, pos_id

    def _validate_xml_and_get_order(self):
        try:
            xml = etree.XML(self.pick_list_xml)
            order = xml
        except Exception as ex:
            raise PickListGenerator.InvalidXml(ex.message), None, sys.exc_info()[2]
        return order

    def _validate_pod_type(self, order):
        if "pod_type" not in order.attrib:
            raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.NoOrderPodTypeMessage)
        pod_type = order.attrib["pod_type"]
        return pod_type

    def _validate_pos_id(self, order):
        if "pos_id" not in order.attrib:
            raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.NoOrderPosIdMessage)
        pos_id = order.attrib["pos_id"]
        return pos_id

    def _validate_sale_type(self, order):
        if "sale_type" not in order.attrib:
            raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.NoOrderSaleTypeMessage)
        sale_type = order.attrib["sale_type"]
        return sale_type

    def _generate_header(self, order):
        if "order_id" not in order.attrib:
            raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.NoOrderIdMessage)
        store = self.store_number
        order_id = order.attrib["order_id"]
        name = self._get_customer_name(order)

        return PickListHeaderDto(self.clock.get_current_time(), order_id, store, name)

    @staticmethod
    def _get_customer_name(order):
        name = None
        name_node = order.find("Properties/Property[@key='CUSTOMER_NAME']")
        if name_node is not None:
            name = name_node.attrib["value"]
        return name

    @staticmethod
    def _generate_body(order):
        # type: (Element) -> PickListBodyDto
        items_node = order.find("Items")
        if items_node is None:
            raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.OrderWithoutItems)

        items = items_node.findall("Item")
        if len(items) == 0:
            raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.OrderWithoutItems)
        pick_list_items = []

        for item in items:
            pick_list_item = PickListItem(item)
            if pick_list_item.description is None:
                raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.ItemWithoutDescription)
            if pick_list_item.qty is None:
                raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.ItemWithoutQuantity)
            if pick_list_item.default_qty is None:
                raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.ItemWithoutDefaultQuantity)
            if pick_list_item.item_type is None:
                raise PickListGenerator.InvalidXml(PickListGenerator.InvalidXml.ItemWithoutItemType)

            pick_list_items.append(pick_list_item)

        return pick_list_items

    class InvalidXml(Exception):
        NoOrderIdMessage = "Order without order_id attribute"
        NoOrderPodTypeMessage = "Order without pod_type attribute"
        NoOrderPosIdMessage = "Order without pos_id attribute"
        OrderWithoutItems = "Order does not have items"
        ItemWithoutDescription = "Item without description: "
        ItemWithoutQuantity = "Item without quantity: "
        ItemWithoutDefaultQuantity = "Item without default quantity: "
        ItemWithoutItemType = "Item without item type: "
        NoOrderSaleTypeMessage = "Order without sale_type attribute"

        def __init__(self, message):
            super(PickListGenerator.InvalidXml, self).__init__(message)
