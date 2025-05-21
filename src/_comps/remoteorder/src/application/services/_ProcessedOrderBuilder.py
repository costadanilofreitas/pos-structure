# -*- coding: utf-8 -*-

from application.apimodel import Item, ProductType
from application.compositiontree import CompositionTree
from application.model import ProcessedOrder, OrderItem
from application.repository import ProductRepository
from application.services import OrderService
from typing import List, Optional


class ProcessedOrderBuilder(object):
    def __init__(self, product_repository, order_service):
        # type: (ProductRepository, OrderService) -> None
        self.product_repository = product_repository
        self.order_service = order_service

        self.all_products = self.product_repository.get_all_products()
        self.all_product_types = self.product_repository.get_all_product_types()

    def build_processed_order(self, remote_order_id, local_order_id, order_trees):
        # type: (int, int, Optional[List[CompositionTree]]) -> ProcessedOrder
        items = []  # type: List[OrderItem]
        if order_trees is not None:
            for order_tree in order_trees:
                items.append(self._build_item_from_composition_tree(order_tree))
        else:
            order = self.order_service.get_order(local_order_id)
            
            if not hasattr(order, "items"):
                raise Exception("Order without items")
            
            for item in order.items:
                items.append(self._build_item_from_api_item(item))

        processed_order = ProcessedOrder(remote_order_id, local_order_id, items)

        return processed_order

    def _build_item_from_composition_tree(self, order_tree):
        # type: (CompositionTree) -> OrderItem
        item = OrderItem()
        item.part_code = order_tree.product.part_code
        item.product_name = self.all_products[int(order_tree.product.part_code)]
        item.quantity = order_tree.product.current_qty
        mw_product_type = self.all_product_types[int(order_tree.product.part_code)]
        if mw_product_type == 0:
            item.product_type = ProductType.Product
        elif mw_product_type == 1:
            item.product_type = ProductType.Option
        else:
            item.product_type = ProductType.Combo

        parts = []
        for order_son in order_tree.sons:
            part = self._build_item_from_composition_tree(order_son)

            parts.append(part)

        item.parts = parts

        return item

    def _build_item_from_api_item(self, api_item):
        # type: (Item) -> OrderItem
        item = OrderItem()
        item.part_code = api_item.part_code
        item.product_name = api_item.product_name
        item.quantity = api_item.quantity
        item.product_type = api_item.product_type

        parts = []
        for son in api_item.sons:
            if son.quantity > 0 or son.default_quantity > 0:
                part = self._build_item_from_api_item(son)
                parts.append(part)

        item.parts = parts

        return item
