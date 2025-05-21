# -*- coding: utf-8 -*-

from application.compositiontree import CompositionType, CompositionTree
from application.model import CurrentOrderItem
from application.repository import OrderRepository
from application.services import PriceService, OrderTakerWrapper
from typing import List


class RemoteOrderItemCreator(object):
    def __init__(self, order_repository, price_service, sell_with_partner_price, order_taker_wrapper, pos_id):
        # type: (OrderRepository, PriceService, bool, OrderTakerWrapper, str) -> None
        self.order_repository = order_repository
        self.price_service = price_service
        self.sell_with_partner_price = sell_with_partner_price
        self.order_taker_wrapper = order_taker_wrapper
        self.pos_id = pos_id

    def create_current_order_items(self, pos_id, order_id, order_trees, delivery):
        # type: (int, int, List[CompositionTree], bool) -> None
        current_order_items = []
        for line_number in range(1, len(order_trees) + 1):
            self._create_current_order_items(current_order_items, order_id, line_number, 0, "1", order_trees[line_number - 1], delivery)

        for item in current_order_items:
            if item.level == 0:
                item_id = item.item_id + "." + item.part_code
                qty = item.included_quantity if item.included_quantity > 0 else item.ordered_quantity
                self.order_taker_wrapper.create_item(self.pos_id, item_id, qty)
                
        self.order_repository.update_current_order_items(pos_id, current_order_items)

    def _create_current_order_items(self, current_order_items, order_id, line_number, level, current_item_id, composition_tree, delivery):
        # type: (List[CurrentOrderItem], int, int, int, unicode, CompositionTree, bool) -> None
        delivery_price = None
        if self.sell_with_partner_price:
            delivery_price = composition_tree.product.price or 0

        if composition_tree.product.type == CompositionType.Combo:
            current_order_item = CurrentOrderItem()
            current_order_item.order_id = order_id
            current_order_item.line_number = line_number
            current_order_item.item_id = current_item_id
            current_order_item.level = level
            current_order_item.part_code = composition_tree.product.part_code
            current_order_item.ordered_quantity = composition_tree.product.current_qty
            current_order_item.last_ordered_quantity = None
            current_order_item.included_quantity = 0
            current_order_item.decremented_quantity = 0
            current_order_item.price_key = self._get_price_key(composition_tree, current_item_id, delivery)
            current_order_item.discount_amount = 0.0
            current_order_item.surcharge_amount = 0.0
            current_order_item.only_flag = 0
            current_order_item.overwritten_unit_price = delivery_price
            current_order_item.default_qty = None

            current_order_items.append(current_order_item)

        elif composition_tree.product.type == CompositionType.Product:
            current_order_item = CurrentOrderItem()
            current_order_item.order_id = order_id
            current_order_item.line_number = line_number
            current_order_item.item_id = current_item_id
            current_order_item.level = level
            current_order_item.part_code = composition_tree.product.part_code
            current_order_item.overwritten_unit_price = delivery_price

            include_product = True
            if composition_tree.product.current_qty == composition_tree.product.default_qty:
                if composition_tree.product.min_qty > 0:
                    current_order_item.ordered_quantity = composition_tree.product.min_qty
                    current_order_item.included_quantity = composition_tree.product.min_qty
                    current_order_item.decremented_quantity = 0
                    current_order_item.default_qty = composition_tree.product.default_qty
                elif composition_tree.parent is not None and composition_tree.parent.product.type == CompositionType.Option and composition_tree.parent.parent is not None and composition_tree.parent.parent.product.type != CompositionType.Product:
                    current_order_item.ordered_quantity = composition_tree.product.current_qty
                    current_order_item.included_quantity = composition_tree.product.current_qty
                    current_order_item.decremented_quantity = 0
                    current_order_item.default_qty = 0
                else:
                    include_product = False
            elif composition_tree.product.default_qty > composition_tree.product.current_qty:
                current_order_item.ordered_quantity = composition_tree.product.current_qty
                current_order_item.included_quantity = 0
                current_order_item.decremented_quantity = composition_tree.product.default_qty - composition_tree.product.current_qty
                current_order_item.default_qty = composition_tree.product.default_qty
            else:
                current_order_item.ordered_quantity = composition_tree.product.current_qty
                current_order_item.included_quantity = composition_tree.product.current_qty
                current_order_item.decremented_quantity = 0
                current_order_item.default_qty = composition_tree.product.default_qty

            current_order_item.last_ordered_quantity = None
            current_order_item.price_key = self._get_price_key(composition_tree, current_item_id, delivery)

            current_order_item.discount_amount = 0.0
            current_order_item.surcharge_amount = 0.0
            current_order_item.only_flag = 0

            if include_product:
                current_order_items.append(current_order_item)

        elif composition_tree.product.type == CompositionType.Option:
            current_order_item = CurrentOrderItem()
            current_order_item.order_id = order_id
            current_order_item.line_number = line_number
            current_order_item.item_id = current_item_id
            current_order_item.level = level
            current_order_item.part_code = composition_tree.product.part_code

            current_order_item.last_ordered_quantity = None
            current_order_item.ordered_quantity = None
            if composition_tree.parent.product.type == CompositionType.Product:
                current_order_item.included_quantity = 0
                current_order_item.decremented_quantity = 0
            else:
                current_order_item.included_quantity = composition_tree.product.current_qty
                current_order_item.decremented_quantity = 0

            current_order_item.price_key = None
            current_order_item.discount_amount = 0.0
            current_order_item.surcharge_amount = 0.0
            current_order_item.only_flag = 0
            current_order_item.overwritten_unit_price = delivery_price
            current_order_item.default_qty = composition_tree.product.min_qty

            current_order_items.append(current_order_item)

        for son in composition_tree.sons:
            code = current_item_id + "." + composition_tree.product.part_code
            self._create_current_order_items(current_order_items, order_id, line_number, level + 1, code, son, delivery)

    def _get_price_key(self, composition_tree, current_item_id, delivery):
        price_list = [u"EI", u"DL"] if not delivery else None
        return self.price_service.get_best_price_key(current_item_id, composition_tree.product.part_code, price_list)
