# -*- coding: utf-8 -*-

import collections
import json
from datetime import datetime
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from enum import Enum
from persistence import Connection
from typing import List, Union, Optional


class Order(object):
    def __init__(self):
        self.order_id = None  # type: Union[int, None]
        self.pos_id = None  # type: Union[int, None]
        self.customer_cpf = None  # type: Union[str, None]
        self.discount_amount = None  # type: Union[float, None]
        self.sale_items = None  # type: Union[List[SaleItem], None]
        self.states = None  # type: Union[List[OrderState], None]
        self.tenders = None  # type: Union[List[OrderTender], None]
        self.tip = None  # type: Union[float, None]
        self.delivery_fee = None  # type: Union[float, None]
        self.discount_amount = None  # type: Union[float, None]
        self.sale_type = None  # type: Union[int, None]


class OrderKey(object):
    def __init__(self, pos_id, order_id):
        self.pos_id = pos_id
        self.order_id = order_id

    def __eq__(self, o):
        if isinstance(o, OrderKey):
            return o.order_id == self.order_id and o.pos_id == self.pos_id

        return False


class OrderParser(object):
    def __init__(self):
        pass

    def parse_order(self, order_xml):
        # type: (ElementTree) -> Order
        pos_id = self._get_pos_id_from_session_id(order_xml.get("sessionId"))
        order_id = int(order_xml.get("orderId"))
        flat_list = self.generate_flat_list(order_xml)
        cpf_element = order_xml.find('.//OrderProperty[@key="CUSTOMER_DOC"]')
        tip = float(order_xml.attrib['tip']) if 'tip' in order_xml.attrib else None
        order = self.generate_order(flat_list, order_id, cpf_element, str(pos_id), tip)
        order.discount_amount = float(order_xml.get('discountAmount') or 0.0)
        order.states = self.parse_order_states(order_xml.findall("StateHistory/State"))
        order.tenders = self.parse_tender(order_xml.findall("TenderHistory/Tender"))
        order.sale_type = int(order_xml.get("saleType"))

        return order

    def generate_flat_list(self, order_xml):
        # type: (ElementTree) ->List[SaleItem]
        sale_items = self.parse_sale_lines(order_xml.findall("SaleLine"))
        sale_trees = self._convert_sale_lines_to_tree(sale_items)
        for sale_tree in sale_trees:
            self._fix_quantity_and_prices(sale_tree)
        flat_list = []  # type: List[SaleItem]
        for sale_tree in sale_trees:
            self._flat_tree_removing_non_priced_items(sale_tree, flat_list)
        return flat_list

    @staticmethod
    def parse_tender(tenders):
        # type: (ElementTree) ->  List[OrderTender]
        tender_list = []  # type: List[OrderTender]
        for tender in tenders:
            amount = float(tender.get("tenderAmount"))
            change = float(tender.get("change") or 0)
            tender_type = int(tender.get("tenderType"))
            tender_detail = tender.get("tenderDetail")
            cnpj_auth = None
            bandeira = None
            auth_code = None
            if tender_detail:
                tender_detail = json.loads(tender_detail)
                cnpj_auth = tender_detail['CNPJAuth'] if 'CNPJAuth' in tender_detail else None
                bandeira = tender_detail['Bandeira'] if 'Bandeira' in tender_detail else None
                auth_code = tender_detail['AuthCode'] if 'AuthCode' in tender_detail else None

            tender_desc = tender.get("tenderDescr")
            if amount > 0:
                order_tender = OrderTender(amount, change, tender_type, tender_desc, cnpj_auth, bandeira, auth_code)
                tender_list.append(order_tender)
        return tender_list

    @staticmethod
    def parse_order_states(states):
        # type: (ElementTree) ->  List[OrderState]
        state_list = []  # type: List[OrderState]
        for state in states:
            timestamp = datetime.strptime(state.get("timestamp"), "%Y-%m-%dT%H:%M:%S.%f")
            timestamp_gmt = datetime.strptime(state.get("timestampGMT"), "%Y-%m-%dT%H:%M:%S.%f")
            order_state = OrderState(state.get("stateId"), state.get("state"), timestamp, timestamp_gmt)
            state_list.append(order_state)
        return state_list

    @staticmethod
    def generate_order(flat_list, order_id, cpf_element, pos_id, tip, delivery_fee=0.0, discount_amount=0.0):
        # type: (List[SaleItem], int, ElementTree, unicode, float) -> Order
        order = Order()
        order.order_id = order_id
        order.pos_id = pos_id
        order.sale_items = flat_list
        order.customer_cpf = cpf_element.get('value') if cpf_element is not None else None
        order.tip = tip
        order.delivery_fee = delivery_fee
        order.discount_amount = discount_amount
        return order

    def parse_sale_lines(self, order_sale_lines):
        sale_items = []  # type: List[SaleItem]
        for order_sale_line in order_sale_lines:
            sale_item = self.create_sale_item(order_sale_line)
            sale_item.type = self.get_sale_item_type(order_sale_line)

            sale_item.multiplied_quantity = float(order_sale_line.get("multipliedQty"))
            if order_sale_line.get("defaultQty") is not None:
                sale_item.default_quantity = int(order_sale_line.get("defaultQty"))

            sale_item.item_discount = self.get_sale_item_item_discount(order_sale_line)
            sale_item.taxes = self.get_sale_item_taxes(order_sale_line)
            sale_item.measure_unit = order_sale_line.get("measureUnit") or "UN"
            sale_items.append(sale_item)
        return sale_items

    @staticmethod
    def create_sale_item(order_sale_line):
        #  type: (ElementTree) -> SaleItem
        sale_item = SaleItem(
            int(order_sale_line.get("lineNumber")),
            int(order_sale_line.get("level")),
            int(order_sale_line.get("partCode")),
            order_sale_line.get("productName"),
            order_sale_line.get("itemId"),
            float(order_sale_line.get("itemPrice")) if order_sale_line.get("itemPrice") is not None else 0.0,
            float(order_sale_line.get("qty") or 0),
            float(order_sale_line.get("unitPrice")) if order_sale_line.get("unitPrice") is not None else 0.0,
            float(order_sale_line.get("addedUnitPrice")) if order_sale_line.get("addedUnitPrice") is not None else 0.0)
        
        if sale_item.item_price > 0 and sale_item.unit_price == 0 and sale_item.added_unit_price == 0:
            sale_item.unit_price = sale_item.item_price / sale_item.quantity
        
        if (sale_item.unit_price > 0 or sale_item.added_unit_price > 0) and sale_item.item_price == 0:
            sale_item.unit_price = 0
            sale_item.added_unit_price = 0
            
        return sale_item

    def get_sale_item_taxes(self, order_sale_line):
        #  type: (ElementTree) -> List[TaxItem]
        taxes = []  # type: (List[TaxItem])
        for tax_item_xml in order_sale_line.findall("TaxItem"):
            tax_item = self._parse_tax_item(tax_item_xml)
            taxes.append(tax_item)
        return taxes

    @staticmethod
    def get_sale_item_item_discount(order_sale_line):
        #  type: (ElementTree) -> float
        if order_sale_line.get("itemDiscount") is not None:
            return float(order_sale_line.get("itemDiscount"))
        return 0.0

    @staticmethod
    def get_sale_item_type(order_sale_line):
        #  type: (ElementTree) -> unicode
        if order_sale_line.get("itemType") == "COMBO":
            return SaleItemType.combo
        elif order_sale_line.get("itemType") == "OPTION":
            return SaleItemType.option
        else:
            return SaleItemType.product

    @staticmethod
    def _parse_tax_item(tax_item_xml):
        # type: (Element) -> TaxItem
        tax_item = TaxItem()
        tax_index = tax_item_xml.get("taxIndex")
        tax_item.tax_name = tax_index.split(";")[0]
        tax_item.tax_index = tax_index.split(";")[1]
        tax_item.tax_rule_id = int(tax_item_xml.get("taxRuleId"))
        tax_item.tax_rate = float(tax_item_xml.get("taxRate"))
        if tax_item_xml.get("taxIncluded") is not None:
            tax_item.tax_included = int(tax_item_xml.get("taxIncluded"))
        tax_item.base_amount_bd = float(tax_item_xml.get("baseAmountBD"))
        tax_item.base_amount_ad = float(tax_item_xml.get("baseAmountAD"))
        tax_item.tax_amount_bd = float(tax_item_xml.get("taxAmountBD"))
        tax_item.tax_amount_ad = float(tax_item_xml.get("taxAmountAD"))

        return tax_item

    def _fix_quantity_and_prices(self, sale_tree, parent=None, grand_parent=None):
        # type: (SaleItem, SaleItem, SaleItem) -> None
        sale_tree = self._fix_quantity_by_ancestors(sale_tree, parent, grand_parent)

        sale_tree.unit_discount = (sale_tree.item_discount / sale_tree.quantity) if sale_tree.quantity > 0 else 0.0
        sale_tree.item_discount = sale_tree.item_discount if sale_tree.quantity > 0 else 0.0

        for tax in sale_tree.taxes:
            tax *= sale_tree.fix_qty_rate

        for son in sale_tree.sons:
            self._fix_quantity_and_prices(son, sale_tree, parent)

    def _fix_quantity_by_ancestors(self, sale_tree, parent, grand_parent):
        # type: (SaleItem, SaleItem, SaleItem) -> SaleItem
        sale_tree = self._verify_product_inside_option_inside_combo(sale_tree, parent, grand_parent)
        sale_tree = self._verify_product_inside_combo(sale_tree, parent)
        sale_tree = self._verify_product_inside_option_inside_product(sale_tree, parent, grand_parent)
        return sale_tree

    @staticmethod
    def _verify_product_inside_option_inside_combo(sale_tree, parent, grand_parent):
        # type: (SaleItem, SaleItem, SaleItem) -> SaleItem
        if sale_tree.type != SaleItemType.product:
            return sale_tree

        if parent is None or parent.type != SaleItemType.option:
            return sale_tree

        if grand_parent is None or grand_parent.type != SaleItemType.combo:
            return sale_tree

        sale_tree.quantity = sale_tree.quantity * grand_parent.multiplied_quantity
        if sale_tree.quantity > 0 and sale_tree.item_price > 0:
            sale_tree.fix_qty_rate = sale_tree.quantity * sale_tree.unit_price / sale_tree.item_price
        sale_tree.item_price = sale_tree.quantity * sale_tree.unit_price
        return sale_tree

    @staticmethod
    def _verify_product_inside_combo(sale_tree, parent):
        # type: (SaleItem, SaleItem) -> SaleItem
        if sale_tree.type != SaleItemType.product:
            return sale_tree

        if parent is None or parent.type != SaleItemType.combo:
            return sale_tree

        sale_tree.quantity = sale_tree.quantity * parent.multiplied_quantity
        if sale_tree.quantity > 0 and sale_tree.item_price > 0:
            sale_tree.fix_qty_rate = sale_tree.quantity * sale_tree.unit_price / sale_tree.item_price
        sale_tree.item_price = sale_tree.quantity * sale_tree.unit_price
        return sale_tree

    @staticmethod
    def _verify_product_inside_option_inside_product(sale_tree, parent, grand_parent):
        # type: (SaleItem, SaleItem, SaleItem) -> SaleItem
        if sale_tree.type != SaleItemType.product:
            return sale_tree

        if parent is None or parent.type != SaleItemType.option:
            return sale_tree

        if grand_parent is None or grand_parent.type != SaleItemType.product:
            return sale_tree

        sale_tree.quantity = (sale_tree.quantity or 0) - (sale_tree.default_quantity or 0)
        sale_tree.quantity *= grand_parent.multiplied_quantity

        sale_tree.unit_price = sale_tree.added_unit_price if sale_tree.added_unit_price > 0 else sale_tree.unit_price
        if sale_tree.quantity > 0 and sale_tree.item_price > 0:
            sale_tree.fix_qty_rate = sale_tree.quantity * sale_tree.unit_price / sale_tree.item_price
        sale_tree.item_price = sale_tree.quantity * sale_tree.unit_price
        return sale_tree

    def _build_item_tree(self, sale_item):
        # type: (SaleItem) -> None
        all_sons = []  # type: List[SaleItem]
        for son in sale_item.sons:
            all_sons.append(son)

        # Adding direct sons from actual item
        current_context = sale_item.item_id + "." + str(sale_item.part_code)
        sale_item.sons = []
        sons_to_remove = []
        self.add_sons(all_sons, current_context, sale_item, sons_to_remove)

        # Removing sons already added from full list
        self.remove_from_list(all_sons, sons_to_remove)

        sons_to_remove = []
        self.add_children(all_sons, sale_item, sons_to_remove)

        if len(sons_to_remove) != len(all_sons):
            # TODO: FIX "1.7100018.7300000.6019.10005000" partCode="8700017" (OPTION 10005000 NOT IN ORDERPICT)
            # raise Exception("Sons not added to any parent")
            pass

        for son in sale_item.sons:
            self._build_item_tree(son)

    @staticmethod
    def add_children(all_sons, sale_item, sons_to_remove):
        for current_son in sale_item.sons:
            current_son_context = current_son.item_id + "." + str(current_son.part_code)
            for son in all_sons:
                if son.item_id.startswith(current_son_context):
                    current_son.sons.append(son)
                    sons_to_remove.append(son)

    @staticmethod
    def remove_from_list(all_sons, sons_to_remove):
        for son in sons_to_remove:
            all_sons.remove(son)

    @staticmethod
    def add_sons(all_sons, current_context, sale_item, sons_to_remove):
        for son in all_sons:
            if son.item_id == current_context:
                sale_item.sons.append(son)
                son.parent = sale_item
                sons_to_remove.append(son)

    def _flat_tree_removing_non_priced_items(self, sale_tree, flat_list):
        # type: (SaleItem, List[SaleItem]) -> None
        if (sale_tree.unit_price or sale_tree.added_unit_price > 0) and sale_tree.quantity > 0:
            flat_list.append(sale_tree)

        for son in sale_tree.sons:
            self._flat_tree_removing_non_priced_items(son, flat_list)

    def _convert_sale_lines_to_tree(self, order_sale_lines):
        # type: (List[SaleItem]) -> List[SaleItem]

        # Find all items with context 1
        level_0_items = filter(lambda x: x.level == 0, order_sale_lines)

        # Insert items into correspondent level 0 lines
        for level_0_item in level_0_items:
            for order_sale_line in order_sale_lines:
                if order_sale_line.line_number != level_0_item.line_number:
                    continue

                if level_0_item != order_sale_line:
                    level_0_item.sons.append(order_sale_line)
                    order_sale_line.parent = level_0_item

        for item in level_0_items:
            self._build_item_tree(item)

        sorted(level_0_items, cmp=lambda item1, item2: item1.line_number - item2.line_number)

        return level_0_items

    @staticmethod
    def _find_level_0_items(sale_items):
        # type: (List[SaleItem]) -> List[SaleItem]
        return filter(lambda x: x.level == 0, sale_items)

    @staticmethod
    def _add_same_line_number(sale_items, parent_items):
        # type: (List[SaleItem], List[SaleItem]) -> None
        for parent_item in parent_items:
            for sale_item in sale_items:
                if sale_item.line_number == parent_item.line_number and sale_item.part_code != parent_item.part_code:
                    parent_item.sons.append(sale_item)
                    sale_item.parent = parent_item

    @staticmethod
    def _add_direct_sons(all_sons, sale_item):
        # type: (List[SaleItem], SaleItem) -> None
        current_context = sale_item.item_id + "." + str(sale_item.part_code)
        sons_to_remove = []
        for son in all_sons:
            if son.item_id == current_context:
                sale_item.sons.append(son)
                son.parent = sale_item
                sons_to_remove.append(son)

        for son in sons_to_remove:
            all_sons.remove(son)

    @staticmethod
    def _add_descendants(all_sons, sale_item):
        # type: (List[SaleItem], SaleItem) -> None
        sons_to_remove = []

        current_son_context = sale_item.item_id + "." + str(sale_item.part_code)
        for son in all_sons:
            if son.item_id.startswith(current_son_context):
                sale_item.sons.append(son)
                sons_to_remove.append(son)

        for son_to_remove in sons_to_remove:
            all_sons.remove(son_to_remove)

    @staticmethod
    def _get_pos_id_from_session_id(session_id):
        # type: (str) -> int
        try:
            pos_id_start_index = session_id.index("pos=")
            pos_id_end_index = session_id.index(",", pos_id_start_index)
            pos_id = session_id[pos_id_start_index + 4:pos_id_end_index]
        except ValueError:
            pos_id = "0"

        return int(pos_id)


class OrderState(object):
    def __init__(self, key, name, timestamp, timestamp_gmt):
        self.key = key  # type: int
        self.name = name  # type: unicode
        self.timestamp = timestamp  # type: datetime
        self.timestamp_gmt = timestamp_gmt  # type: datetime

    def __eq__(self, o):
        if isinstance(o, OrderState):
            return o.key == self.key \
                   and o.name == self.name \
                   and o.timestamp == self.timestamp \
                   and o.timestamp_gmt == self.timestamp_gmt

        return False


class OrderTender(object):
    def __init__(self, amount, change, tender_type, descr, cnpj_auth, bandeira, auth_code):
        self.amount = amount  # type: float
        self.change = change  # type: float
        self.type = tender_type  # type: int
        self.descr = descr  # type: unicode
        self.cnpj_auth = cnpj_auth  # type: unicode
        self.bandeira = bandeira  # type: unicode
        self.auth_code = auth_code

    def __eq__(self, o):
        if isinstance(o, OrderTender):
            return o.amount == self.amount \
                   and o.change == self.change \
                   and o.type == self.type \
                   and o.descr == self.descr \
                   and o.cnpj_auth == self.cnpj_auth \
                   and o.bandeira == self.bandeira \
                   and o.auth_code == self.auth_code

        return False


class PosConnection(object):
    def __init__(self, pos_id, connection):
        # type: (str, Connection) -> None
        self.pos_id = pos_id
        self.connection = connection

    def __del__(self):
        return self.connection.__del__()

    def close(self):
        return self.connection.close()

    def is_multi_instance(self):
        return self.connection.is_multi_instance()

    def set_dbname(self, db_name):
        # type: (str) -> None
        return self.connection.set_dbname(db_name)

    def query(self, sql):
        return self.connection.query(sql)

    def pquery(self, procedure_name, **kargs):
        return self.connection.pquery(procedure_name, **kargs)

    def select(self, sql):
        return self.connection.select(sql)

    def pselect(self, procedure_name, **kargs):
        return self.connection.pselect(procedure_name, **kargs)

    def escape(self, string):
        return self.connection.escape(string)

    def transaction_start(self):
        return self.connection.transaction_start()

    def transaction_end(self):
        return self.connection.transaction_end()

    def transaction_mode_get(self):
        return self.connection.transaction_mode_get()

    def transaction_mode_set(self, mode):
        return self.connection.transaction_mode_set(mode)


class SaleItemType(object):
    combo = "Combo"
    option = "Option"
    product = "Product"


class SaleItem(object):
    def __init__(self, line_number=None, level=None, part_code=None, product_name=None, item_id=None, item_price=None,
                 quantity=None, unit_price=None, added_unit_price=0.0, item_discount=0.0, unit_discount=0.0,
                 item_additional=0.0, unit_additional=0.0, measure_unit="UN"):
        # type: (int, int, int, unicode, Optional[unicode], float, float, float, float, float, Optional[str]) -> None
        self.line_number = line_number
        self.level = level
        self.part_code = part_code
        self.product_name = product_name  # type: unicode
        self.item_id = item_id
        self.item_price = item_price
        self.quantity = quantity
        self.unit_price = unit_price  # type: float
        self.added_unit_price = added_unit_price  # type: float
        self.item_discount = item_discount
        self.unit_discount = unit_discount
        self.item_additional = item_additional
        self.unit_additional = unit_additional
        self.measure_unit = measure_unit

        self.fix_qty_rate = 1

        self.default_quantity = None  # type: None
        self.type = None  # type: unicode
        self.multiplied_quantity = None  # type: int

        self.parent = None  # type: SaleItem
        self.sons = []  # type: List[SaleItem]
        self.taxes = []  # type: List[TaxItem]

    def get_tax_item(self, tax_name):
        # type: (unicode) -> Optional[TaxItem]
        for tax_item in self.taxes:
            if tax_item.tax_name == tax_name:
                unit_price = self.unit_price if self.unit_price > 0 else self.added_unit_price
                multiplier = round(self.quantity / (tax_item.base_amount_bd / unit_price))
                return tax_item * multiplier

        return None

    def __str__(self):
        return ("lineNumber: " + str(self.line_number) + ", " +
                "level: " + str(self.level) + ", " +
                "part_code: " + str(self.part_code) + ", " +
                "item_id: " + self.item_id + ", " +
                "quantity: " + str(self.quantity) + ", " +
                "unit_price: " + str(self.unit_price) + ", " +
                "item_price: " + str(self.item_price) + ", " +
                "taxes: " + str(self.taxes) + ", " +
                "sons: " + str(self.sons) + ", " +
                "parent: " + str(self.parent) + ", ")

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, SaleItem):
            return self.level == other.level and self.item_id == other.item_id and self.part_code == other.part_code

        return False

    def __hash__(self):
        return hash((self.level, self.item_id, self.part_code))


class Tax(object):
    def __init__(self, code, name, rate, fiscal_index, tax_processor, params):
        # type: (unicode, unicode, float, unicode, unicode) -> None
        self.code = code
        self.name = name
        self.rate = rate
        self.fiscal_index = fiscal_index
        self.tax_processor = tax_processor
        self.params = params


class TaxItem(object):
    def __init__(self):
        self.tax_rule_id = None  # type: unicode
        self.tax_index = None  # type: unicode
        self.tax_name = None  # type: unicode
        self.tax_code = None  # type: unicode
        self.base_amount_bd = None  # type: float
        self.base_amount_ad = None  # type: float
        self.tax_amount_bd = None  # type: float
        self.tax_amount_ad = None  # type: float
        self.tax_included = None  # type: float
        self.tax_rate = None  # type: float

    def __str__(self):
        return ("taxRuleId: " + str(self.tax_rule_id) + ", " +
                "taxIndex: " + str(self.tax_index) + ", " +
                "taxName: " + str(self.tax_name) + ", " +
                "taxRate: " + str(self.tax_rate) + ", " +
                "baseAmountBd: " + str(self.base_amount_bd) + ", " +
                "baseAmountAd: " + str(self.base_amount_ad) + ", " +
                "taxAmountBd: " + str(self.tax_amount_bd) + ", " +
                "taxAmountAd: " + str(self.tax_amount_ad) + ", " +
                "taxIncluded: " + str(self.tax_included))

    def __repr__(self):
        return self.__str__()

    def __mul__(self, o):
        self.base_amount_ad *= o
        self.base_amount_bd *= o
        self.tax_amount_ad *= o
        self.tax_amount_bd *= o

        return self


class TenderType(object):
    cash = 0
    credit = 1
    debit = 2
    external_card = 3


class SaleType(object):
    EAT_IN = 0
    TAKE_OUT = 1
    DRIVE_THRU = 2
    DELIVERY = 3
    ONLINE = 4
    PICKUP = 5
    PHONE = 6
    CATERING = 7


class XmlTenderType(object):
    cash = 1
    credit = 3
    debit = 4
    others = 99


class XmlTenderTypeFromPOSMapper(object):
    @staticmethod
    def get(tender_type):
        # type: (int) -> int
        if tender_type == TenderType.cash:
            return XmlTenderType.cash
        if tender_type == TenderType.credit:
            return XmlTenderType.credit
        if tender_type == TenderType.debit:
            return XmlTenderType.debit
        return XmlTenderType.others


class POSTenderTypeFromXmlMapper(object):
    @staticmethod
    def get(tender_type):
        # type: (int) -> Union[int, None]
        if tender_type == XmlTenderType.cash:
            return TenderType.cash
        if tender_type == XmlTenderType.credit:
            return TenderType.credit
        if tender_type == XmlTenderType.debit:
            return TenderType.debit
        return XmlTenderType.others


class DeliveryTenderTypes(Enum):
    SPOON_ROCKET = 27
    IFOOD = 28
    LOGGI = 29
    APP = 30
    UBER_EATS = 31
    GLOVO = 32

    @staticmethod
    def list_tender_values():
        delivery_tender_types = DeliveryTenderTypes  # type: collections.Iterable
        return [x.value for x in delivery_tender_types]


class TableStatus(Enum):
    UNMAPPED_STATUS = 0
    AVAILABLE = 1
    WAITING_TO_BE_SEATED = 2
    SEATED = 3
    IN_PROGRESS = 4
    LINKED = 5
    TOTALIZED = 6
    CLOSED = 7

    @staticmethod
    def list_values():
        return [x.value for x in TableStatus]

    @staticmethod
    def get_status_label(status):
        # type: (int) -> Union[str, None]
        if status not in [x for x in TableStatus.list_values()]:
            return TableStatus.Unmaped.name

        for table_status in TableStatus:
            if status == table_status.value:
                return table_status.name
