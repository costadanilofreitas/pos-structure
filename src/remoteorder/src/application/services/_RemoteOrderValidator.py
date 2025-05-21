# -*- coding: utf-8 -*-

import functools
import json
from xml.etree import ElementTree as eTree

from application.compositiontree import CompositionTreeBuilder, CompositionTree
from application.customexception import OrderValidationException, OrderValidationError, ProductUnavailableException, \
    InvalidValueException
from application.model import RemoteOrder, PriceWarning, RemoteOrderModelJsonEncoder
from application.services import CompositionTreeValidator, OrderPriceCalculator, WarningEmitter, WarningType
from helper import round_half_away_from_zero
from typing import List, Optional


class RemoteOrderValidator(object):
    def __init__(self, composition_tree_builder, composition_validator, order_price_calculator, warning_emitter, validate_delivery_price, validate_delivery_value):
        # type: (CompositionTreeBuilder, CompositionTreeValidator, OrderPriceCalculator, WarningEmitter, bool, float) -> None # noqa

        self.composition_tree_builder = composition_tree_builder
        self.composition_validator = composition_validator
        self.order_price_calculator = order_price_calculator
        self.warning_emitter = warning_emitter
        self.validate_delivery_price = validate_delivery_price
        self.validate_delivery_price_value = validate_delivery_value

    def validate_order(self, remote_order, unavailable_items=None):
        # type: (RemoteOrder, List[unicode]) -> ([List[CompositionTree], Optional[Exception]])

        exception = None
        if unavailable_items is None:
            unavailable_items = []

        if not remote_order.items:
            raise OrderValidationException(OrderValidationError.OrderWithNoItens, "The remote order has no items")

        single_qty_remote_items = self.make_single_qty_remote_items(remote_order)

        all_items_tress = []
        for item in single_qty_remote_items:
            try:
                composition_tree = self.composition_tree_builder.get_composition_tree(item.part_code,
                                                                                      unavailable_list=unavailable_items)
                if composition_tree.product.enabled is False:
                    raise ProductUnavailableException(OrderValidationError.InvalidProductPartCode,
                                                      "$RUPTURED_PRODUCT|{}".format(composition_tree.product.part_code))
                new_composition_tree = self.composition_validator.validate_order_composition(composition_tree, item)

                all_items_tress.append(new_composition_tree)
            except Exception as ex:
                if not exception:
                    exception = ex

        return all_items_tress, exception

    def make_single_qty_remote_items(self, remote_order):
        single_qty_remote_items = []
        for item in remote_order.items:
            father_qty = item.quantity
            for _ in range(0, father_qty):
                single_qty_remote_items.append(self.make_single_qty_item(item))

        return single_qty_remote_items

    def make_single_qty_item(self, item):
        item.quantity = 1 if item.quantity > 0 else -1
        new_parts = []
        for part in item.parts:
            part_quantity = part.quantity
            for _ in range(0, abs(part_quantity)):
                new_parts.append(self.make_single_qty_item(part))
        item.parts = new_parts
        return item

    @staticmethod
    def already_processed(remote_order_id, order_pict):
        # type: (unicode, eTree.XML) -> bool

        for prop in order_pict.findall("CustomOrderProperties/OrderProperty"):
            key = prop.get("key")
            if key == "RETRANSMIT_%s" % remote_order_id:
                return True
        return False

    def _find_in_sale_lines(self, composition_tree, sale_lines, current_line_number=None):
        item_found = False
        for line in sale_lines:
            line_number = line.get('lineNumber')
            product_part_code = composition_tree.product.part_code
            if line.get('partCode') == product_part_code and current_line_number in [None, line_number]:
                # found product, continue checking sons, if any
                item_found = True
                for son in composition_tree.sons:
                    try:
                        self._find_in_sale_lines(son, sale_lines, line_number)
                    except Exception: # noqa
                        item_found = False
                composition_tree.product.name = line.get('productName')
                composition_tree.product.current_qty = line.get('qty')
        if not item_found:
            raise Exception('Item %s not found in order.' % composition_tree.product.part_code)

    def validate_order_contains(self, order_trees, order_pict):
        # type: (List[CompositionTree], eTree.XML) -> None

        sale_lines = order_pict.findall("Order/SaleLine")
        for composition_tree in order_trees:
            self._find_in_sale_lines(composition_tree, sale_lines)

    def validate_order_price(self, remote_order, order_trees):
        # type: (RemoteOrder, List[CompositionTree]) -> None

        is_app_order = remote_order.partner == "app" and remote_order.pickup.type != "delivery"

        total_price = self.order_price_calculator.calculate_order_price(order_trees, is_app_order)
        if round(total_price, 2) != round(remote_order.sub_total + remote_order.discount_amount, 2):
            price_warning = PriceWarning()
            price_warning.remote_order_id = remote_order.id
            price_warning.remote_order_items_value = remote_order.sub_total
            price_warning.local_order_items_value = total_price
            price_warning_json = json.dumps(price_warning, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)
            self.warning_emitter.emit_warn(WarningType.PriceWarning, price_warning_json)

        if self.validate_delivery_price or is_app_order:
            total_payments = functools.reduce(lambda x, y: x + y.value, remote_order.tenders, 0)
            end_value, start_value = self.get_range_delivery(total_price)
            total_payments = round_half_away_from_zero(total_payments, 2)
            if total_payments < start_value or total_payments > end_value:
                raise InvalidValueException(
                    OrderValidationError.InternalError, "Invalid purchase value: Expected {}; But Was {}".format(
                        total_price, total_payments))

    def get_range_delivery(self, total_price):
        value = self.validate_delivery_price_value
        start_value = round_half_away_from_zero(total_price - value, 2)
        end_value = round_half_away_from_zero(total_price + value, 2)
        return end_value, start_value
